# Python Imports in This Repo (`cmdstash` vs `src.cmdstash`)

This note explains why imports in this project are written as:

- `from cmdstash import cli`

and **not**:

- `from src.cmdstash import cli`

## The short answer

In a `src` layout project, `src/` is a filesystem container, not part of the package name.
The package name is the directory **inside** `src`, which is `cmdstash`.

So the import path is `cmdstash`, not `src.cmdstash`.

## Mental model: how Python resolves imports

When Python sees `import X`, it searches directories listed in `sys.path` in order.
If Python can find a package/module named `X` in one of those directories, import succeeds.
Otherwise you get `ModuleNotFoundError`.

For this repo, import success depends on whether Python can see:

- `<repo>/src` on `sys.path` (so `cmdstash` is importable from `<repo>/src/cmdstash`)

## Why tests can use `from cmdstash ...`

When you run tests through the project tooling (for example `uv run pytest`), the environment is set up so the project package is importable as `cmdstash`.

That is why this works in tests:

- `from cmdstash import cli`

## Why `from src.cmdstash` is usually wrong

`src` is typically not a Python package namespace you want to expose. It is just a directory convention that keeps import behavior honest during development/packaging.

Using `from src.cmdstash ...` couples code to repository layout and often fails once installed from wheel/sdist, where users import the installed package as `cmdstash`.

## How `pyproject.toml` affects this

`pyproject.toml` controls build/install metadata and entry points, not the literal import syntax in your code.

In this repo, important parts are:

- project name: `cmdstash`
- console script: `cmdstash = "cmdstash.cli:main"`
- version path: `src/cmdstash/__about__.py`

Those settings reinforce that the importable package is `cmdstash`.

## Project bootstrap timeline (this repo)

Based on git history, this is the likely setup order:

1. Repo/docs were initialized.
2. A later commit added `pyproject.toml` and `src/cmdstash/*` together.
3. Dependency/environment sync was run (`uv.lock` appears in that same phase).
4. The local project was installed editable into `.venv`.
5. Editable install wrote a `.pth` file in site-packages that points to `<repo>/src`.
6. Python startup reads that `.pth`, so `<repo>/src` appears on `sys.path`.

The key point: `uv sync` did not "invent" `src/`; `src/` already existed in the repo.
`uv` installed the project and made Python aware of that existing directory.

## Exactly how `uv` knew to add `src/`

`uv` orchestrates installation, but the build backend (`hatchling`) defines package mapping.

High-level sequence:

1. `uv` sees a local project (`pyproject.toml` with `[project]` + `[build-system]`).
2. It performs an editable install of that local project into `.venv` (unless told not to install the project).
3. It asks `hatchling` to build editable metadata/wheel hooks.
4. `hatchling` detects package code under `src/cmdstash`.
5. Editable install materializes as a site-packages `.pth` file containing `<repo>/src`.
6. Python reads `.pth` at startup and appends that path to `sys.path`.

So "who added `src/` to the import path?" is effectively:

- You/agent added `src/cmdstash` to the repo.
- `hatchling` decided that is the package source root.
- `uv` installed it editable and wrote the `.pth` into the environment.
- Python consumed `.pth` and updated `sys.path`.

## Quick checks when confused

- Print active import path:
  - `uv run python -c "import sys, pprint; pprint.pp(sys.path)"`
- Show where `cmdstash` is imported from:
  - `uv run python -c "import cmdstash; print(cmdstash.__file__)"`
- Show the path injection file:
  - `uv run python -c "import pathlib,sys; sp=pathlib.Path(sys.prefix)/'lib'/'python3.14'/'site-packages'; print([p for p in sp.glob('*.pth')])"`

## Common `ModuleNotFoundError` causes in src-layout projects

1. Running Python from an environment where project package is not installed and `src/` is not on `sys.path`.
2. Running tests/commands with a different interpreter than the one managed by the project tooling.
3. Importing with the wrong module path (for example `src.cmdstash`).
4. Naming collisions (a local file named `cmdstash.py` shadowing the real package).

## Practical rules for this repo

- In code and tests, import from `cmdstash`, never `src.cmdstash`.
- Prefer project commands (`uv run ...`) so interpreter/path setup is consistent.
- If you see `ModuleNotFoundError`, first verify you are using the repo's expected command flow (`uv run pytest`, `uv run cmdstash --help`).
