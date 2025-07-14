import time
from functools import lru_cache
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.middlewares import add_process_time_header

from .api import api_router
from .config import settings

app = FastAPI()
app.include_router(api_router)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)
