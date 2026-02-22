# Platformdirs Notes

Quick reference for how `cmdstash` should choose filesystem locations across macOS, Linux, and Windows.

## Why use `platformdirs`

- It applies platform conventions automatically.
- It avoids hardcoding OS-specific paths.
- It supports both string and `pathlib.Path` APIs.
- It can create directories for you when needed (`ensure_exists=True`).

## Core APIs we care about

For this project, prefer the `*_path` variants (they return `Path` objects).

- `user_data_path(appname, ensure_exists=...)`
  - Use for user-specific persistent app data.
  - This is where `cmdstash` stores the SQLite database.
- `user_config_path(appname, ensure_exists=...)`
  - Use for user-editable configuration files (settings, profiles).
  - Useful later if we add a config file.
- `user_cache_path(appname, ensure_exists=...)`
  - Use for disposable/rebuildable data.
  - Safe to delete; app should be able to recreate.
- `user_state_path(appname, ensure_exists=...)`
  - Use for persistent state that is not primary user data.
  - Mostly relevant on Linux/XDG-style setups.
- `user_log_path(appname, ensure_exists=...)`
  - Use for log files if we add file logging later.

## How cmdstash uses it (Step 3 decision)

- Data directory:
  - `user_data_path("cmdstash", ensure_exists=True)`
- Database file:
  - `<user_data_path>/cmdstash.db`

This keeps DB storage in the expected per-user application data location on each OS.

## Practical rule of thumb

- Primary durable user data (our command stash DB): `user_data_path`
- User-tweakable settings: `user_config_path`
- Temporary performance artifacts: `user_cache_path`
- Logs: `user_log_path`

## Notes about naming

You may see references to "get user data dir/path" in docs or conversation.
In `platformdirs`, the canonical helpers are `user_data_dir()` (string) and
`user_data_path()` (`Path`).
