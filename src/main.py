from functools import lru_cache
from fastapi import FastAPI

from .api import api_router
from .config import settings

print(settings)
app = FastAPI()
app.include_router(api_router)
