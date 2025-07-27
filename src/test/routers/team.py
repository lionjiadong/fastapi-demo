from fastapi import APIRouter, Query, Request
from sqlmodel import select
from src.database.core import SessionDep
from src.test.models.team import TeamOut, Team, TeamBase

team_router = APIRouter(
    prefix="/team",
    tags=["team"],
)


@team_router.get("/", response_model=list[TeamOut])
async def read_teams(
    request: Request,
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    teams = (await session.exec(select(Team).offset(offset).limit(limit))).all()
    return teams
