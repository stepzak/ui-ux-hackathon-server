from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI



def create_app(title: str, version: str, openapi_url) -> FastAPI:

    app = FastAPI(title=title, version=version, openapi_url=openapi_url)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app