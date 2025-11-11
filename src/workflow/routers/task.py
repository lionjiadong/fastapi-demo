from fastapi import APIRouter, Depends, Query
from sqlmodel import select

from src.auth.models.auth import get_current_user
from src.database.core import SessionDep
from src.workflow.models.task import Task

task_router = APIRouter(
    prefix="/task",
    tags=["task"],
    dependencies=[Depends(get_current_user)],
)


@task_router.get("/", response_model=list[Task])
async def read_tasks(
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    roles = (await session.exec(select(Task).offset(offset).limit(limit))).all()
    return roles
