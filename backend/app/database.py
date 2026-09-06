import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _resolve_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        db_path = BASE_DIR / "database" / "sales.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{db_path.as_posix()}"
    if url.startswith("sqlite:///"):
        path_part = url.replace("sqlite:///", "", 1)
        if path_part:
            p = Path(path_part) if Path(path_part).is_absolute() else BASE_DIR / path_part
            p.parent.mkdir(parents=True, exist_ok=True)
            url = f"sqlite:///{p.as_posix()}"
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
