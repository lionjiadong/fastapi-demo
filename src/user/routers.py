from typing import Sequence
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from pydantic import ValidationError
from sqlmodel import Session, select
from src.auth.routers import get_current_user
from src.database.core import SessionDep
from src.user.models.users import User, UserBase, UserIn, UserOut

user_router = APIRouter(
    prefix="/users",
    tags=["user"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.active:
        return current_user
    raise HTTPException(status_code=400, detail="Inactive user")


@user_router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)) -> User:
    return current_user


@user_router.get("/me/items")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]


@user_router.post("/user/")
def create_user(user: UserIn, session: SessionDep) -> UserOut:
    # print(user)
    # user.hashed_password = user.hash_pwd()
    # db_user = None
    # try:
    db_user = User.model_validate(user.model_dump())
    # except ValidationError as e:
    #     print(e)
    # print(db_user)
    # session.add(db_user)
    # session.commit()
    # session.refresh(db_user)
    return db_user


@user_router.get("/user/{user_id}")
def read_user(user_id: int, session: SessionDep) -> UserOut:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.get("/users/")
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
) -> Sequence[User]:
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


# @user_router.get("/heroes/{hero_id}")
# def read_hero(hero_id: int, session: SessionDep) -> Hero:
#     hero = session.get(Hero, hero_id)
#     if not hero:
#         raise HTTPException(status_code=404, detail="Hero not found")
#     return hero


# @user_router.delete("/heroes/{hero_id}")
# def delete_hero(hero_id: int, session: SessionDep):
#     hero = session.get(Hero, hero_id)
#     if not hero:
#         raise HTTPException(status_code=404, detail="Hero not found")
#     session.delete(hero)
#     session.commit()
#     return {"ok": True}
