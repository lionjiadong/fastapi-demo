from .hero import Hero, HeroBase, HeroOut  # noqa: F401
from .team import Team, TeamBase, TeamOut  # noqa: F401

HeroOut.model_rebuild()
TeamOut.model_rebuild()
