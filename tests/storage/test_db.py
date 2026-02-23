import sqlite3

from cmdstash.storage import db
from cmdstash.storage.migrations import MIGRATIONS


def _table_names(connection: sqlite3.Connection) -> set[str]:
    rows = connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    return {row[0] for row in rows}


def _applied_versions(connection: sqlite3.Connection) -> list[str]:
    rows = connection.execute("SELECT version FROM schema_migrations ORDER BY version").fetchall()
    return [row[0] for row in rows]


def test_initialize_database_creates_schema_and_tracks_migrations(tmp_path) -> None:
    db_path = tmp_path / "cmdstash.db"

    applied = db.initialize_database(db_path)

    assert applied == [migration.version for migration in MIGRATIONS]

    connection = sqlite3.connect(db_path)
    try:
        assert {
            "commands",
            "tags",
            "command_tags",
            "command_examples",
            "schema_migrations",
        }.issubset(_table_names(connection))
        assert _applied_versions(connection) == [migration.version for migration in MIGRATIONS]
    finally:
        connection.close()


def test_initialize_database_is_idempotent(tmp_path) -> None:
    db_path = tmp_path / "cmdstash.db"

    db.initialize_database(db_path)
    applied = db.initialize_database(db_path)

    assert applied == []

    connection = sqlite3.connect(db_path)
    try:
        count = connection.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0]
        assert count == len(MIGRATIONS)
    finally:
        connection.close()


def test_initialize_database_upgrades_from_partial_migration_state(tmp_path) -> None:
    db_path = tmp_path / "cmdstash.db"
    first_migration = MIGRATIONS[0]

    connection = sqlite3.connect(db_path)
    try:
        connection.execute(
            """
            CREATE TABLE schema_migrations (
                version TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        for statement in first_migration.statements:
            connection.execute(statement)
        connection.execute(
            "INSERT INTO schema_migrations (version, description) VALUES (?, ?)",
            (first_migration.version, first_migration.description),
        )
        connection.commit()
    finally:
        connection.close()

    applied = db.initialize_database(db_path)

    assert applied == [migration.version for migration in MIGRATIONS[1:]]

    verify_connection = sqlite3.connect(db_path)
    try:
        assert _applied_versions(verify_connection) == [
            migration.version for migration in MIGRATIONS
        ]
    finally:
        verify_connection.close()


def test_open_connection_closes_after_context_exit(tmp_path) -> None:
    db_path = tmp_path / "cmdstash.db"

    with db.open_connection(db_path) as connection:
        assert connection.execute("SELECT 1").fetchone()[0] == 1

    try:
        connection.execute("SELECT 1")
    except sqlite3.ProgrammingError:
        pass
    else:
        msg = "Expected connection to be closed after context manager exits."
        raise AssertionError(msg)
