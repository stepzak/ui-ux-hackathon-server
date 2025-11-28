from sqlalchemy import select

from src.shared.core.settings import settings
from src.shared.dependencies.db import db_dep
from src.shared.models import VersionFile
from src.shared.schemas.versions import VersionMetrics
from src.shared.utils.app_factory import create_app

app = create_app(title = "Metrics Service", version = settings.API_V1_STR, openapi_url = settings.API_V1_STR+"/docs")

@app.get("/{version}", response_model = VersionMetrics)
async def get_metrics(version: str, db: db_dep):
    stmt = select(VersionFile).where(VersionFile.version_name == version)
    result = await db.execute(stmt)
    res = result.scalar_one_or_none()
    if res:
        return res.meta