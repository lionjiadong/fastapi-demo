from typing import Annotated

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
