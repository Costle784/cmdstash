# Build + Packaging Notes

Working notes for Python packaging and release flow.

## `pyproject.toml` → `[build-system]` (what it is)

The `[build-system]` table tells packaging tools **how to build this project into distribution artifacts**
(a source distribution and a wheel). It is defined by PEP 517/518 and is primarily consumed by tools like `pip`, `build`, and `uv build`.

Current config:

```toml
[build-system]
requires = ["hatchling>=1.27.0"]
build-backend = "hatchling.build"
```

Meaning:
- `requires`: build-time dependencies that must be installed in an isolated environment before building.
- `build-backend`: the Python object implementing the build hooks (here, Hatchling).

In practice for this repo:
- `uv build` reads `[build-system]`.
- `uv` creates an isolated build environment.
- It installs `hatchling>=1.27.0` there.
- It asks `hatchling.build` to produce `dist/*.tar.gz` (sdist) and `dist/*.whl` (wheel).

## How this relates to PyPI

- PyPI hosts the built artifacts; it does **not** build your project for you.
- The backend selected in `[build-system]` controls what gets packaged.
- Uploading to PyPI means uploading files from `dist/` that came from that backend.
- Installers (`pip install cmdstash`) then install from those artifacts.

## What `[build-system]` does *not* control

- Project runtime metadata like name/dependencies/entrypoints (that is `[project]`).
- Your test/lint tooling configuration.
- Versioning strategy itself (though backend-specific config can read where version lives).

## `pyproject.toml` -> `[project.scripts]` (why local command runs work)

`[project.scripts]` defines console entrypoints. This is what makes `uv run cmdstash ...` work in local development.

For this repo:

```toml
[project.scripts]
cmdstash = "cmdstash.cli:main"
```

Meaning:
- command name: `cmdstash`
- target callable: `cmdstash.cli:main`

Practical effect:
- when the project is installed into the venv, tooling generates a small launcher script named `cmdstash`
- running `uv run cmdstash --help` executes that launcher, which imports and calls `cmdstash.cli.main`

Without `[project.scripts]`, `uv run cmdstash ...` would not work by command name; you would need module-style execution like `uv run python -m cmdstash`.

## Core Commands

- Build artifacts: `uv build`
- Validate metadata (future): `uv run twine check dist/*`

## Reminders

- Keep metadata in `pyproject.toml` (PEP 621).
- Ensure console entrypoint for `cmdstash` remains correct.
- Keep dependencies minimal and explicit.
- If build fails, confirm `[build-system]` backend and version constraints are valid.

## To Capture As Decisions

- Version bump workflow
- Release checklist
- PyPI publish commands
