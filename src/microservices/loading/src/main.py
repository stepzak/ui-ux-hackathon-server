import os
import pyarrow.parquet as pq

from fastapi import Form, UploadFile, File
from src.shared.core.settings import settings
from src.shared.dependencies.db import db_dep
from src.shared.models import VersionFile
from src.shared.utils.app_factory import create_app
from src.shared.utils.extractors import extract_metrics_from_hits_chunks, extract_metrics_from_visits_chunks

UPLOAD_DIR = settings.UPLOAD_DIR
app = create_app("Loading Service", version = settings.VERSION, openapi_url = settings.API_V1_STR+"/docs")

@app.post("/", status_code=201)
async def upload_files(db: db_dep,
        version: str = Form(..., description="Название версии, например: v1, v2, new_ui"),
    hits_file: UploadFile = File(..., description="Файл с хитами (CSV)"),
    visits_file: UploadFile = File(..., description="Файл с визитами (CSV)")):
    upload_dir = UPLOAD_DIR / version

    os.makedirs(upload_dir, exist_ok=True)
    print(upload_dir)

    upload_hits_file = upload_dir / "hits.parquet"
    upload_visits_file = upload_dir / "visits.parquet"
    upload_visits_file.touch(exist_ok=True)
    upload_hits_file.touch(exist_ok=True)
    with open(upload_hits_file, "wb") as f:
        f.write(await hits_file.read())

    with open(upload_visits_file, "wb") as f:
        f.write(await visits_file.read())

    #TODO: PARSE FILES
    f_hits = pq.ParquetFile(upload_hits_file)
    metrics = extract_metrics_from_hits_chunks(f_hits, 150000)
    f_visits = pq.ParquetFile(upload_visits_file)
    metrics.update(extract_metrics_from_visits_chunks(f_visits, 150000))
    obj = VersionFile(version_name = version, path_to_hits= str(upload_hits_file), path_to_visits = str(upload_visits_file), meta = metrics)
    db.add(obj)
    await db.commit()
    return metrics
    #except Exception as e:
     #   raise HTTPException(detail = str(e), status_code = 400)
