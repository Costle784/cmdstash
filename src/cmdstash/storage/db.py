from collections.abc import Iterator
from contextlib import contextmanager
import sqlite3
from pathlib import Path

from cmdstash.config import get_default_db_path
from cmdstash.storage.migrations import apply_pending_migrations


def _resolve_db_path(db_path: Path | None = None) -> Path:
    """Resolve the target database path and ensure parent directory exists."""
    resolved = db_path if db_path is not None else get_default_db_path()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def initialize_database(db_path: Path | None = None) -> list[str]:
    """Create/upgrade the database schema and return newly applied migrations."""
    connection = sqlite3.connect(_resolve_db_path(db_path))
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        return apply_pending_migrations(connection)
    finally:
        connection.close()


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    """Open a SQLite connection and ensure migrations are applied first."""
    connection = sqlite3.connect(_resolve_db_path(db_path))
    connection.execute("PRAGMA foreign_keys = ON")
    apply_pending_migrations(connection)
    return connection


@contextmanager
def open_connection(db_path: Path | None = None) -> Iterator[sqlite3.Connection]:
    """Yield a migrated connection and always close it."""
    connection = connect(db_path)
    try:
        yield connection
    finally:
        connection.close()
