from typing import TYPE_CHECKING

from sqlmodel import Relationship, SQLModel, Field
from .link import HeroTeamLink


if TYPE_CHECKING:
    from .team import Team


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    teams: list["Team"] = Relationship(back_populates="hero", link_model=HeroTeamLink)
