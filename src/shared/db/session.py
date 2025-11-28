from sqlalchemy.engine.url import URL
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from src.shared.core.settings import settings

DRIVER = settings.DRIVER
DRIVER_ALEMBIC = settings.DRIVER_ALEMBIC
DATABASE = settings.DATABASE
USERNAME = settings.POSTGRES_USER
PASSWORD = settings.POSTGRES_PASSWORD
HOST = settings.DATABASE_HOST
PORT = settings.DATABASE_PORT

url = URL.create(
    drivername=DRIVER,
    username=USERNAME,
    password=PASSWORD,
    host=HOST,
    database=DATABASE,
    port=PORT,
)


url_alembic  = URL.create(
    drivername=DRIVER_ALEMBIC,
    username=USERNAME,
    password=PASSWORD,
    host=HOST,
    database=DATABASE,
    port=PORT,
)

engine = create_async_engine(
    url = url,
    future=True,
    poolclass=NullPool,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

async def get_db() -> AsyncSession:
    """
    Асинхронная зависимость для получения сессии БД
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError:
            await session.rollback()

            raise
        finally:
            await session.close()