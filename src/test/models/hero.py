from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from .links import HeroTeamLink

if TYPE_CHECKING:
    from .team import Team


class HeroBase(SQLModel):
    name: str


class HeroOut(HeroBase):

    teams: list["Team"] = []


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    teams: list["Team"] = Relationship(back_populates="heroes", link_model=HeroTeamLink)
