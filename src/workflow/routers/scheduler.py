from fastapi import APIRouter, Depends, Query
from sqlmodel import select

from src.auth.models.auth import get_current_user
from src.auth.models.user import User
from src.database.core import SessionDep
from src.workflow.models.scheduler import PeriodicTask

periodic_task_router = APIRouter(
    prefix="/periodic_task_",
    tags=["periodic_task"],
    dependencies=[Depends(get_current_user)],
)


@periodic_task_router.get("/", response_model=list[PeriodicTask])
async def read_periodic_tasks(
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    roles = (await session.exec(select(PeriodicTask).offset(offset).limit(limit))).all()
    return roles


@periodic_task_router.post("/", response_model=PeriodicTask)
async def create_periodic_task(
    data: PeriodicTask,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """创建角色"""
    print(f"create_periodic_task: {data}")
    print(f"create_periodic_task: {data.model_dump()}")
    periodic_task = PeriodicTask.model_validate(data.model_dump())
    return await periodic_task.create(session, current_user)
