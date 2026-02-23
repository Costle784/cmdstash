from dataclasses import dataclass
import sqlite3


@dataclass(frozen=True)
class Migration:
    """A forward-only SQL migration step."""

    version: str
    description: str
    statements: tuple[str, ...]


MIGRATIONS: tuple[Migration, ...] = (
    Migration(
        version="0001_initial_schema",
        description="Create command metadata tables.",
        statements=(
            """
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY,
                command TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS command_tags (
                command_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (command_id, tag_id),
                FOREIGN KEY (command_id) REFERENCES commands(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS command_examples (
                id INTEGER PRIMARY KEY,
                command_id INTEGER NOT NULL,
                example TEXT NOT NULL,
                position INTEGER NOT NULL,
                FOREIGN KEY (command_id) REFERENCES commands(id) ON DELETE CASCADE,
                UNIQUE(command_id, position)
            )
            """,
        ),
    ),
    Migration(
        version="0002_add_tag_lookup_index_on_command_tags",
        description="Add tag-to-command lookup index for joins and facets.",
        statements=("CREATE INDEX IF NOT EXISTS idx_command_tags_tag_id ON command_tags(tag_id)",),
    ),
)


def ensure_migration_table(connection: sqlite3.Connection) -> None:
    """Create the migration tracking table if it does not exist."""
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            description TEXT NOT NULL,
            applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def get_applied_versions(connection: sqlite3.Connection) -> set[str]:
    """Return migration versions that have already been applied."""
    rows = connection.execute("SELECT version FROM schema_migrations").fetchall()
    return {row[0] for row in rows}


def apply_pending_migrations(connection: sqlite3.Connection) -> list[str]:
    """Apply all unapplied migrations and return applied version numbers."""
    ensure_migration_table(connection)
    applied_versions = get_applied_versions(connection)
    newly_applied: list[str] = []

    for migration in MIGRATIONS:
        if migration.version in applied_versions:
            continue

        with connection:
            for statement in migration.statements:
                connection.execute(statement)
            connection.execute(
                """
                INSERT INTO schema_migrations (version, description)
                VALUES (?, ?)
                """,
                (migration.version, migration.description),
            )
        newly_applied.append(migration.version)

    return newly_applied
