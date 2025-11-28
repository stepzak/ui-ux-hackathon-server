import pathlib

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "My App"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/v1"

    DRIVER: str
    DATABASE: str
    DATABASE_HOST: str
    DATABASE_PORT: str
    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    DRIVER_ALEMBIC: str

    HOST_SERVER: str = "0.0.0.0"
    PORT_SERVER: int = 8000

    UPLOAD_DIR: pathlib.Path



    class Config:
        env_file = ".env"


settings = Settings()