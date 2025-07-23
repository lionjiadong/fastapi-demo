from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError


from src.exceptions import validation_exception_handler
from src.middlewares import add_process_time_header

from .api import api_router
from .config import settings


app = FastAPI(
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ],
    exception_handlers={
        ValidationError: validation_exception_handler,
    },
    docs_url=None,
    redoc_url=None,
    openapi_url="/openapi.json",
    swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(api_router)
