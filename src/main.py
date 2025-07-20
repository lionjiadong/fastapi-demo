import time
from functools import lru_cache
from fastapi import FastAPI, Request
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
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
)
app.include_router(api_router)
