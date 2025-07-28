from fastapi import APIRouter, Depends, Query
from sqlmodel import select
from src.auth.models.auth import get_current_user
from src.database.core import SessionDep
from src.auth.models.user import User, UserCreate, UserOut, UserUpdate

user_router = APIRouter(
    prefix="/users",
    tags=["user"],
    dependencies=[Depends(get_current_user)],
)


@user_router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@user_router.get("/", response_model=list[UserOut])
async def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    users = (await session.exec(select(User).offset(offset).limit(limit))).all()
    return users


@user_router.post("/", response_model=UserOut)
async def create_user(
    data: UserCreate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    user = User.model_validate(data.model_dump())
    return await user.create(session, current_user)


@user_router.get("/{user_id}", response_model=UserOut)
async def read_user(user_id: int, session: SessionDep):
    return await User.get_by_id(session, user_id)


@user_router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    data: UserUpdate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    user = await User.get_by_id(session, user_id)
    return await user.update(
        session=session,
        data=data.model_dump(exclude_unset=True),
        current_user=current_user,
    )


@user_router.delete("/{user_id}")
async def delete_user(
    user_id: int, session: SessionDep, current_user: User = Depends(get_current_user)
):
    user = await User.get_by_id(session, user_id)
    await user.delete(session=session, current_user=current_user)
    return {"ok": True}
