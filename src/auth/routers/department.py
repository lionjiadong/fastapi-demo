from fastapi import APIRouter, Depends, Query
from sqlmodel import select

from src.auth.models.auth import get_current_user
from src.auth.models.department import Department
from src.auth.models.user import User
from src.auth.schemas.department import (
    DepartmentCreate,
    DepartmentOutLinks,
    DepartmentUpdate,
)
from src.database.core import SessionDep

department_router = APIRouter(
    prefix="/department",
    tags=["department"],
    dependencies=[Depends(get_current_user)],
)


@department_router.get("/", response_model=list[DepartmentOutLinks])
async def read_departments(
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    """获取多个角色"""
    roles = (await session.exec(select(Department).offset(offset).limit(limit))).all()
    return roles


@department_router.post("/", response_model=DepartmentOutLinks)
async def create_department(
    data: DepartmentCreate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """创建角色"""
    department = Department.model_validate(data)
    return await department.create(session, current_user)


@department_router.get("/{department_id}", response_model=DepartmentOutLinks)
async def read_department(
    department_id: int,
    session: SessionDep,
):
    """获取单个角色"""
    return await Department.get_by_id(session, department_id)


@department_router.patch("/{department_id}", response_model=DepartmentOutLinks)
async def update_department(
    department_id: int,
    data: DepartmentUpdate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """更新角色"""
    department = await Department.get_by_id(session, department_id)
    return await department.update(
        session=session,
        data=data.model_dump(exclude_unset=True),
        current_user=current_user,
    )


@department_router.delete("/{department_id}")
async def delete_department(
    department_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """删除角色"""
    department = await Department.get_by_id(session, department_id)
    await department.delete(session=session, current_user=current_user)
    return {"ok": True}
