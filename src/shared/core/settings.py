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
    PORT_LOADING: int
    PORT_METRICS: int

    UPLOAD_DIR: pathlib.Path

    OPEN_AI_KEY: str
    OPEN_AI_FOLDER: str
    OPEN_AI_MODEL: str = "qwen3-235b-a22b-fp8/latest"
    class Config:
        env_file = ".env"


settings = Settings()