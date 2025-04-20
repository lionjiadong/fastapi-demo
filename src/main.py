from fastapi import Depends, FastAPI
from src.auth.routers import token_router
from src.user.routers import user_router

app = FastAPI()
app.include_router(token_router)
app.include_router(user_router)
# app.mount("/test", app=token_router)