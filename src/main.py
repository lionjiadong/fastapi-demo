from fastapi import FastAPI
from src.auth.routers import token_router
from src.user.routers import user_router
from .db import create_db_and_tables



app = FastAPI(lifespan=create_db_and_tables)

app.include_router(token_router)
app.include_router(user_router)
# app.mount("/test", app=token_router)