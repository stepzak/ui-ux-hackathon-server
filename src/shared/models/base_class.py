from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from sqlalchemy.sql.sqltypes import DateTime


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    #public_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), unique=True, default = uuid7, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default = lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:

        return cls.__name__.lower() + 's'
