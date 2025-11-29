from sqlalchemy import select
from src.shared.core.settings import settings
from src.shared.dependencies.db import db_dep
from src.shared.models import VersionFile, VersionComparison
from src.shared.schemas.versions import VersionMetrics
from src.shared.utils.app_factory import create_app
from src.shared.utils.comparators import compare_versions_full
from src.shared.utils.extractors import extract_patterns_and_aggregates_from_full_data, \
    extract_metrics_from_hits_chunks, extract_metrics_from_visits_chunks
from src.shared.utils.gpt_analyser import analyze_comparison_with_gpt
import pyarrow.parquet as pq

app = create_app(title = "Metrics Service", version = settings.API_V1_STR, openapi_url = settings.API_V1_STR+"/docs")

@app.get("/cmp/{v1_name}/{v2_name}")
async def compare_metrics(v1_name: str, v2_name: str, db: db_dep):
    print(f"Comparing {v1_name} and {v2_name}")
    stmt1 = select(VersionFile).where(VersionFile.version_name == v1_name)
    stmt2 = select(VersionFile).where(VersionFile.version_name == v2_name)

    res1: VersionFile = (await db.execute(stmt1)).scalar_one_or_none()
    res2: VersionFile = (await db.execute(stmt2)).scalar_one_or_none()

    hits1, visits1 = res1.path_to_hits, res1.path_to_visits
    hits2, visits2 = res2.path_to_hits, res2.path_to_visits
    print(f"Extracting {v1_name}")
    v1_data = extract_patterns_and_aggregates_from_full_data(hits1, visits1)
    print(f"Extracting {v2_name}", flush=True)
    v2_data = extract_patterns_and_aggregates_from_full_data(hits2, visits2)
    print(f"Comparing {v1_name} and {v2_name}")
    comparison = compare_versions_full(v1_data, v2_data)
    print(f"Sending {v1_name} and {v2_name} to LLM", flush=True)
    analysis = analyze_comparison_with_gpt(comparison)
    new_obj = VersionComparison(version_first=v1_name, version_second=v2_name, results = analysis)
    db.add(new_obj)
    await db.commit()

    return analysis

@app.get("/{version}", response_model = VersionMetrics)
async def get_metrics(version: str, db: db_dep):
    print(version)
    stmt = select(VersionFile).where(VersionFile.version_name == version)
    result = await db.execute(stmt)
    res = result.scalar_one_or_none()
    if res:
        return res.meta

@app.put("/{version}", response_model = VersionMetrics)
async def update_metrics(version: str, db: db_dep):
    stmt = select(VersionFile).where(VersionFile.version_name == version)
    result = await db.execute(stmt)
    res: VersionFile = result.scalar_one_or_none()
    if res:
        h_t = pq.ParquetFile(res.path_to_hits)
        metrics_hits = extract_metrics_from_hits_chunks(h_t, 150_000)
        v_t = pq.ParquetFile(res.path_to_visits)
        metrics_visits = extract_metrics_from_visits_chunks(v_t, 150_000)
        metrics_hits.update(metrics_visits)
        res.meta = metrics_hits
        db.add(res)
        await db.commit()
        return res.meta