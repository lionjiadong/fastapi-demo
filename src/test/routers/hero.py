from fastapi import APIRouter, Query, Request
from sqlmodel import select
from src.database.core import SessionDep
from src.test.models.hero import HeroOut, Hero, HeroBase

hero_router = APIRouter(
    prefix="/hero",
    tags=["hero"],
)


@hero_router.get("/", response_model=list[HeroOut])
async def read_heros(
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    heros = (await session.exec(select(Hero).offset(offset).limit(limit))).all()
    return heros
