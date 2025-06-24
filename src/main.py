from fastapi import FastAPI
from src.auth.routers import token_router
from src.user.routers import user_router

# from src.database.core import lifespan


app = FastAPI()

app.include_router(token_router)
app.include_router(user_router)
