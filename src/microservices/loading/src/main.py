from fastapi import Form, UploadFile, File

from src.shared.core.settings import settings
from src.shared.utils.app_factory import create_app

app = create_app("Loading Service", version = settings.VERSION, openapi_url = settings.API_V1_STR+"/docs")

@app.post("/")
async def upload_files(version: str = Form(..., description="Название версии, например: v1, v2, new_ui"),
    hits_file: UploadFile = File(..., description="Файл с хитами (CSV)"),
    visits_file: UploadFile = File(..., description="Файл с визитами (CSV)")):
    ...