from typing import Annotated
from collections.abc import AsyncGenerator
from fastapi import Depends
from sqlmodel import Session, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.config import settings


database_url: str = settings.database_url
engine = create_async_engine(database_url)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


# def get_session():
#     with Session(engine) as session:
#         yield session
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


# SessionDep = Annotated[Session, Depends(get_session)]
SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
