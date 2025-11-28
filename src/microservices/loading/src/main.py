from fastapi import Form, UploadFile, File
from sqlalchemy import select
from starlette.exceptions import HTTPException
from src.shared.utils.analysis import extract_metrics_from_parquet
from src.shared.core.settings import settings
from src.shared.dependencies.db import db_dep
from src.shared.models import VersionFile
from src.shared.utils.app_factory import create_app

UPLOAD_DIR = settings.UPLOAD_DIR
app = create_app("Loading Service", version = settings.VERSION, openapi_url = settings.API_V1_STR+"/docs")

@app.post("/", status_code=201)
async def upload_files(db: db_dep,
        version: str = Form(..., description="Название версии, например: v1, v2, new_ui"),
    hits_file: UploadFile = File(..., description="Файл с хитами (CSV)"),
    visits_file: UploadFile = File(..., description="Файл с визитами (CSV)")):
    #try:
    upload_dir = UPLOAD_DIR / version

    upload_dir.mkdir(parents = True, exist_ok = True)

    upload_hits_file = upload_dir / "hits.parquet"
    upload_visits_file = upload_dir / "visits.parquet"

    with open(upload_hits_file, "wb") as f:
        f.write(await hits_file.read())

    with open(upload_visits_file, "wb") as f:
        f.write(await visits_file.read())

    #TODO: PARSE FILES
    metrics = extract_metrics_from_parquet(upload_hits_file, upload_visits_file)
    obj = VersionFile(version_name = version, path_to_hits= str(upload_hits_file), path_to_visits = str(upload_visits_file), meta = metrics)
    db.add(obj)
    await db.commit()
    #except Exception as e:
     #   raise HTTPException(detail = str(e), status_code = 400)

@app.get("/{version}")
async def get_metrics(version: str, db: db_dep):
    stmt = select(VersionFile).where(VersionFile.version_name == version)
    result = await db.execute(stmt)
    res = result.scalar_one_or_none()
    if res:
        return res.meta
