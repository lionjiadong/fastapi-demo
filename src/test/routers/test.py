from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import select
from src.auth.models.auth import get_current_user
from src.database.core import SessionDep
from src.test.models.test import TestBase, TestField
from src.auth.models.user import User

test_router = APIRouter(
    prefix="/test",
    tags=["test"],
)


@test_router.get("/", response_model=list[TestField])
async def read_tests(
    request: Request,
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    teams = (await session.exec(select(TestField).offset(offset).limit(limit))).all()
    return teams


@test_router.post("/", response_model=TestField)
async def create_role(
    data: TestBase,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    role = TestField.model_validate(data.model_dump())
    return await role.create(session, current_user)
