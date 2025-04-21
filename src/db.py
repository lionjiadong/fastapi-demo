from typing import Annotated
from fastapi import Depends, FastAPI
from sqlmodel import SQLModel, Session, create_engine


database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_demo"
engine = create_engine(database_url)
def create_db_and_tables(app: FastAPI =None):
    SQLModel.metadata.create_all(engine)
def get_session():
    with Session(engine) as session:
        yield session
SessionDep = Annotated[Session, Depends(get_session)]
def lifespan():
    create_db_and_tables()