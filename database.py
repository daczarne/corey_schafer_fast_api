from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.orm.session import Session


SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"

engine: Engine = create_engine(
    url = SQLALCHEMY_DATABASE_URL,
    connect_args = {
        "check_same_thread": False,
    },
)

SessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = engine,
)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session]:
    with SessionLocal() as db:
        yield db
