from fastapi import Form, UploadFile, File
from sqlalchemy import select
from starlette.exceptions import HTTPException
from src.shared.utils.analysis import extract_metrics_from_csv
from src.shared.core.settings import settings
from src.shared.dependencies.db import db_dep
from src.shared.models import VersionFile
from src.shared.utils.app_factory import create_app

UPLOAD_DIR_HITS = settings.UPLOAD_DIR_HITS
UPLOAD_DIR_VISITS = settings.UPLOAD_DIR_VISITS
app = create_app("Loading Service", version = settings.VERSION, openapi_url = settings.API_V1_STR+"/docs")

@app.post("/", status_code=201)
async def upload_files(db: db_dep,
        version: str = Form(..., description="Название версии, например: v1, v2, new_ui"),
    hits_file: UploadFile = File(..., description="Файл с хитами (CSV)"),
    visits_file: UploadFile = File(..., description="Файл с визитами (CSV)")):
    #try:
    upload_hits_dir = UPLOAD_DIR_HITS / version
    upload_visits_dir = UPLOAD_DIR_VISITS / version

    upload_hits_dir.mkdir(parents = True, exist_ok = True)
    upload_visits_dir.mkdir(parents = True, exist_ok = True)

    upload_hits_file = upload_hits_dir / "hits.csv"
    upload_visits_file = upload_visits_dir / "visits.csv"

    with open(upload_hits_file, "w", encoding="utf-8") as f:
        content = await hits_file.read()
        f.write(content.decode("utf-8-sig"))

    with open(upload_visits_file, "w", encoding="utf-8") as f:
        content = await visits_file.read()
        f.write(content.decode("utf-8-sig"))

    #TODO: PARSE FILES
    metrics = extract_metrics_from_csv(upload_hits_file, upload_visits_dir)
    obj = VersionFile(version, upload_hits_file, upload_visits_file, metrics)
    db.add(obj)
    await db.commit()
    #except Exception as e:
     #   raise HTTPException(detail = str(e), status_code = 400)

@app.get("/{version}")
async def get_metrics(version: str, db: db_dep):
    stmt = select(VersionFile).where(VersionFile.version_name == version)
    result = await db.execute(stmt)
    return result.first().meta
