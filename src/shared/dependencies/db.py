from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.shared.db.session import get_db

db_dep = Annotated[AsyncSession, Depends(get_db)]