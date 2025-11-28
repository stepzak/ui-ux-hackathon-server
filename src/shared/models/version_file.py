from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.models.base_class import Base

class VersionFile(Base):
    version_name: Mapped[str] = mapped_column(primary_key=True)
    path_to_hits: Mapped[str]
    path_to_visits: Mapped[str]
    meta: Mapped[dict] = mapped_column(JSONB)

class VersionComparison(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    version_first: Mapped[str] = mapped_column(index = True)
    version_second: Mapped[str] = mapped_column(index = True)
    results: Mapped[dict] = mapped_column(JSONB)