from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from src.database.core import SessionDep
from src.auth.models.role import RoleOut, RoleBase, Role

role_router = APIRouter(
    prefix="/role",
    tags=["role"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}, 401: {"description": "未提供TOKEN"}},
)


@role_router.get("/", response_model=list[RoleOut])
async def read_roles(
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    roles = session.exec(select(Role).offset(offset).limit(limit)).all()
    return roles


@role_router.get("/{role_id}", response_model=RoleOut)
async def read_role(role_id: int, session: SessionDep):
    role = session.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@role_router.post("/", response_model=RoleOut)
async def create_role(role: RoleBase, session: SessionDep):
    db_role = Role.model_validate(role.model_dump())
    session.add(db_role)
    session.commit()
    session.refresh(db_role)
    return db_role


@role_router.patch("/{role_id}", response_model=RoleOut)
async def update_role(role_id: int, role: RoleBase, session: SessionDep):
    role_db = session.get(Role, role_id)
    if not role_db:
        raise HTTPException(status_code=404, detail="Role not found")
    role_data = role.model_dump(exclude_unset=True)
    role_db.sqlmodel_update(role_data)
    session.add(role_db)
    session.commit()
    session.refresh(role_db)
    return role_db


@role_router.delete("/{role_id}")
async def delete_role(role_id: int, session: SessionDep):
    role = session.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    session.delete(role)
    session.commit()
    return {"ok": True}
