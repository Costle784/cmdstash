from importlib.metadata import PackageNotFoundError, metadata
from pathlib import Path

from platformdirs import user_data_path

APP_NAME = "cmdstash"
DB_FILENAME = "cmdstash.db"


def get_default_data_dir() -> Path:
    """Return the per-user data directory for cmdstash, creating it if needed."""
    return user_data_path(APP_NAME, ensure_exists=True)


def get_default_db_path() -> Path:
    """Return the default SQLite database path for cmdstash."""
    return get_default_data_dir() / DB_FILENAME


def get_supported_python_specifier() -> str:
    """Return the declared supported Python range from package metadata."""
    try:
        requires_python = metadata(APP_NAME).get("Requires-Python")
    except PackageNotFoundError:
        return "Unknown"
    return requires_python or "Unknown"
