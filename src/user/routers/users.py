from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from src.user.routers.auth import get_current_user
from src.database.core import SessionDep
from src.user.models.users import User, UserBase, UserIn, UserOut

user_router = APIRouter(
    prefix="/users",
    tags=["user"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}, 401: {"description": "未提供TOKEN"}},
)


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.active:
        return current_user
    raise HTTPException(status_code=400, detail="Inactive user")


@user_router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@user_router.get("/", response_model=list[UserOut])
async def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@user_router.get("/{user_id}", response_model=UserOut)
async def read_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.post("/", response_model=UserOut)
async def create_user(user: UserIn, session: SessionDep):
    db_user = User.model_validate(user.model_dump())
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@user_router.patch("/{user_id}", response_model=UserOut)
async def update_user(user_id: int, user: UserBase, session: SessionDep):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.model_dump(exclude_unset=True)
    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db


@user_router.delete("/{user_id}")
async def delete_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}
