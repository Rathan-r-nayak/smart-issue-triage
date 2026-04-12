from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator


SQLALCHEMY_DATABASE_URL = "postgresql://postgres:supersecretpassword@localhost:5432/smart_issue_triage"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autoflush=False, bind=engine)


Base = declarative_base()


def get_db() -> Generator:
    """
    FastAPI will call this function every time an HTTP request comes in.
    It opens a fresh database session, pauses (yield) while the router does its work,
    and safely closes the connection when the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()