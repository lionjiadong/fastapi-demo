import re
from typing import Annotated

from sqlalchemy.ext.declarative import declarative_base, declared_attr
from fastapi import Depends
from sqlmodel import Session, create_engine, inspect


database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_demo"
engine = create_engine(database_url)
# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)
def get_session():
    with Session(engine) as session:
        yield session
SessionDep = Annotated[Session, Depends(get_session)]

def resolve_table_name(name):
    """Resolves table names to their mapped names."""
    names = re.split("(?=[A-Z])", name)  # noqa
    return "_".join([x.lower() for x in names if x])

class CustomBase:
    __repr_attrs__ = []
    __repr_max_length__ = 15

    @declared_attr
    def __tablename__(self):
        return resolve_table_name(self.__name__)

    def dict(self):
        """Returns a dict representation of a model."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @property
    def _id_str(self):
        ids = inspect(self).identity
        if ids:
            return "-".join([str(x) for x in ids]) if len(ids) > 1 else str(ids[0])
        else:
            return "None"

    @property
    def _repr_attrs_str(self):
        max_length = self.__repr_max_length__

        values = []
        single = len(self.__repr_attrs__) == 1
        for key in self.__repr_attrs__:
            if not hasattr(self, key):
                raise KeyError(
                    "{} has incorrect attribute '{}' in __repr__attrs__".format(self.__class__, key)
                )
            value = getattr(self, key)
            wrap_in_quote = isinstance(value, str)

            value = str(value)
            if len(value) > max_length:
                value = value[:max_length] + "..."

            if wrap_in_quote:
                value = "'{}'".format(value)
            values.append(value if single else "{}:{}".format(key, value))

        return " ".join(values)

    def __repr__(self):
        # get id like '#123'
        id_str = ("#" + self._id_str) if self._id_str else ""
        # join class name, id and repr_attrs
        return "<{} {}{}>".format(
            self.__class__.__name__,
            id_str,
            " " + self._repr_attrs_str if self._repr_attrs_str else "",
        )


Base = declarative_base(cls=CustomBase)
metadata = Base.metadata