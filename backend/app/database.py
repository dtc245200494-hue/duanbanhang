import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _resolve_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        return f"sqlite:///{(BASE_DIR / 'database' / 'sales.db').as_posix()}"
    if url.startswith("sqlite:///"):
        path_part = url.replace("sqlite:///", "", 1)
        if path_part and not Path(path_part).is_absolute():
            url = "sqlite:///" + (BASE_DIR / path_part).as_posix()
    return url


DATABASE_URL = _resolve_database_url()

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
