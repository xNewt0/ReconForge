"""SQLAlchemy database setup.

Note: This project uses SQLite by default.
We keep migrations lightweight by applying additive ALTER TABLE changes on startup.
"""

from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

from .config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    echo=settings.debug,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency to provide a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _column_exists(conn, table: str, column: str) -> bool:
    rows = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
    return any(r[1] == column for r in rows)  # r[1] = name


def _table_exists(conn, table: str) -> bool:
    row = conn.execute(
        text("SELECT name FROM sqlite_master WHERE type='table' AND name=:t"),
        {"t": table},
    ).fetchone()
    return row is not None


def apply_migrations() -> None:
    """Apply lightweight additive migrations for SQLite."""
    if not settings.database_url.startswith("sqlite"):
        # For non-sqlite, a proper migration tool should be used.
        return

    with engine.begin() as conn:
        # scans: return_code + error
        if _table_exists(conn, "scans"):
            if not _column_exists(conn, "scans", "return_code"):
                conn.execute(text("ALTER TABLE scans ADD COLUMN return_code INTEGER"))
            if not _column_exists(conn, "scans", "error"):
                conn.execute(text("ALTER TABLE scans ADD COLUMN error TEXT"))


def init_db():
    """Create all tables and apply additive migrations."""
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    apply_migrations()
