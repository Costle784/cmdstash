# Python Imports

This note explains why this repo uses:

- `from cmdstash import cli`

and not:

- `from src.cmdstash import cli`

## TL;DR

- `src/` is a folder layout choice, not part of the import path.
- Import path uses the package name (`cmdstash`), not repository folders.
- Python imports from `sys.path`.
- Editable installs usually add a pointer to `src/` (for fast local iteration).
- Non-editable installs copy built package files into `site-packages`.

If you remember one thing: **imports are about what Python can see on `sys.path`, not where files sit in Git.**

## Core mental model

When Python sees `import X`, it checks each directory in `sys.path` in order:

1. If `X` exists in one of those directories, import succeeds.
2. If not, you get `ModuleNotFoundError`.

For this repo, `import cmdstash` works when `<repo>/src` is on `sys.path`, because package code is in `src/cmdstash`.

## Why `src.cmdstash` is wrong

`src` is a container directory. It is not the package namespace.

- Right: `from cmdstash import cli`
- Wrong: `from src.cmdstash import cli`

Using `src.cmdstash` tightly couples imports to local repo layout and usually fails after normal installation.

## The missing link: `[project].name`

The most important connection is:

- `pyproject.toml` has `[project].name = "cmdstash"`
- Build tooling uses that name during default package selection
- `src/cmdstash/__init__.py` matches that name
- Result: import path is `cmdstash.*`

So yes, project metadata directly influences what package is considered "the project package."

## How `uv` + `hatchling` made `src/` importable

In this repo, the practical sequence is:

1. `src/cmdstash` exists in the repository.
2. `uv` installs the local project into `.venv`.
3. `hatchling` (build backend) selects package source from project metadata + layout.
4. Editable install creates a `.pth` file in `site-packages` pointing at `<repo>/src`.
5. Python startup reads that `.pth`, adding `<repo>/src` to `sys.path`.

So `uv` did not invent `src/`; it wired Python to already-existing source code.

## Editable vs non-editable (practical)

This choice is about workflow, not whether you publish to PyPI.

Editable install:

- Source of truth: working tree (`src/...`)
- Update behavior: edits are reflected immediately
- Mechanism: pointers/import hooks from `site-packages` to local source
- Best for: local development

Non-editable install:

- Source of truth: installed package files in `site-packages`
- Update behavior: edits require reinstall
- Mechanism: install from built artifacts (wheel/sdist)
- Best for: release/CI verification of "real install" behavior

Common healthy pattern:

- Use editable for day-to-day coding.
- Occasionally run non-editable checks to catch packaging surprises.

## Where `site-packages` is

`site-packages` is the environment's install directory for Python distributions.

In this repo's venv, it is typically:

- `.venv/lib/python3.14/site-packages`

Quick checks:

- `uv run python -m site`
- `uv run python -c "import site; print(site.getsitepackages())"`

You can inspect files there directly. This is often the fastest way to debug import issues.

## Why checkout-first CI feels like "magic"

Typical flow:

1. Checkout code from Git.
2. Create/select environment.
3. Install (`poetry install`, `uv sync`, `pip install ...`).
4. Start API/worker/cron process.

Because tools do most setup implicitly, teams rarely say "editable" or "non-editable" out loud.
It usually feels seamless until path/layout assumptions change.

## Common causes of `ModuleNotFoundError`

1. Wrong interpreter/environment is active.
2. Project is not installed and `src/` is not on `sys.path`.
3. Import path is wrong (`src.cmdstash` instead of `cmdstash`).
4. Local naming collision (for example `cmdstash.py` shadowing package).
5. Build config omits a package that editable mode accidentally made visible.

## Cross-tool truth (Poetry, uv, setuptools, PDM, Hatch)

Tool commands differ, but the core model is the same:

- metadata + backend decide what is packaged
- install mode decides how code is made importable
- Python ultimately imports from what is visible on `sys.path`

## Quick debug recipe (copy/paste)

1. Show interpreter and `sys.path`:
   - `uv run python -c "import sys, pprint; print(sys.executable); pprint.pp(sys.path)"`
2. Show what file actually got imported:
   - `uv run python -c "import cmdstash; print(cmdstash.__file__)"`
3. Show pointer files in site-packages:
   - `uv run python -c "import pathlib,sys; sp=pathlib.Path(sys.prefix)/'lib'/'python3.14'/'site-packages'; print(list(sp.glob('*.pth')))"`.

## Practical rules for this repo

- In code/tests, import `cmdstash`, never `src.cmdstash`.
- Prefer repo commands (`uv run ...`) so env/path behavior is consistent.
- If imports fail, verify interpreter first, then `sys.path`, then package install state.

## Import path vs executable command (important distinction)

These are related but different:

- Import path: `import cmdstash` works because Python can find package code on `sys.path`.
- Executable command: `cmdstash ...` works because `[project.scripts]` maps command name to a callable.

For this repo, both must be correct:

- `src/cmdstash/...` + install state make imports work.
- `[project.scripts] cmdstash = "cmdstash.cli:main"` makes the `cmdstash` shell command available in the environment.
