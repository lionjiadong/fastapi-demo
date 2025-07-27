from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from .links import HeroTeamLink

if TYPE_CHECKING:
    from .hero import Hero


class TeamBase(SQLModel):
    name: str


class TeamOut(TeamBase):
    heroes: list["Hero"] = []


class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    heroes: list["Hero"] = Relationship(back_populates="teams", link_model=HeroTeamLink)
