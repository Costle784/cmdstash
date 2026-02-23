from importlib.metadata import PackageNotFoundError, metadata
from pathlib import Path

from platformdirs import user_data_path

APP_NAME = "cmdstash"
DB_FILENAME = "cmdstash.db"


def get_default_data_dir(*, data_dir_resolver=user_data_path) -> Path:
    """Return the per-user data directory for cmdstash, creating it if needed."""
    return data_dir_resolver(APP_NAME, ensure_exists=True)


def get_default_db_path(*, data_dir: Path | None = None) -> Path:
    """Return the default SQLite database path for cmdstash."""
    resolved_data_dir = data_dir if data_dir is not None else get_default_data_dir()
    return resolved_data_dir / DB_FILENAME


def get_supported_python_specifier(*, metadata_reader=metadata) -> str:
    """Return the declared supported Python range from package metadata."""
    try:
        requires_python = metadata_reader(APP_NAME).get("Requires-Python")
    except PackageNotFoundError:
        return "Unknown"
    return requires_python or "Unknown"
