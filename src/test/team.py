from typing import TYPE_CHECKING

from sqlmodel import Relationship, SQLModel, Field
from .link import HeroTeamLink


if TYPE_CHECKING:
    from .hero import Hero


class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    heroes: list["Hero"] = Relationship(
        # secondary="hero",
        back_populates="team",
        link_model=HeroTeamLink,
    )
