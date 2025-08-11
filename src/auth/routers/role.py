from fastapi import APIRouter, Depends, Query
from sqlmodel import select
from src.database.core import SessionDep
from src.auth.models.auth import get_current_user
from src.auth.models.user import User
from src.auth.schemas.role import RoleOut, RoleCreate, RoleOutLinks, RoleUpdate
from src.auth.models.role import Role

role_router = APIRouter(
    prefix="/role",
    tags=["role"],
    dependencies=[Depends(get_current_user)],
)


@role_router.get("/", response_model=list[RoleOutLinks])
async def read_roles(
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    roles = (await session.exec(select(Role).offset(offset).limit(limit))).all()
    return roles


@role_router.post("/", response_model=RoleOutLinks)
async def create_role(
    data: RoleCreate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    role = Role.model_validate(data.model_dump())
    return await role.create(session, current_user)


@role_router.get("/{role_id}", response_model=RoleOutLinks)
async def read_role(role_id: int, session: SessionDep):
    return await Role.get_by_id(session, role_id)


@role_router.patch("/{role_id}", response_model=RoleOutLinks)
async def update_role(
    role_id: int,
    data: RoleUpdate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    role = await Role.get_by_id(session, role_id)
    return await role.update(
        session=session,
        data=data.model_dump(exclude_unset=True),
        current_user=current_user,
    )


@role_router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    role = await Role.get_by_id(session, role_id)
    await role.delete(session=session, current_user=current_user)
    return {"ok": True}
