"""
Impressionist AI Services Application Package
"""

__version__ = "0.1.0"

from fastapi import FastAPI
from app.config import Config
from app.api import api_router


def create_app() -> FastAPI:
    app = FastAPI()
    app.config = Config()

    app.include_router(api_router, prefix="/api")

    @app.get("/")
    def root():
        return "This is the backend API of Impressionist Program from DDDG."

    return app
