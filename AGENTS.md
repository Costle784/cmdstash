---
description: 
alwaysApply: true
---

# AGENTS.md — cmdstash

This repository is a **learning project**. Optimize for **clarity, small steps, and explanation** over speed.
Every change should be easy to review and understand.
Favor readability and human comprehension above all else: choose clear names,
straightforward code, and enough context/documentation to make intent obvious.

This project is intended to be **published to PyPI**, so structure the repo accordingly (src-layout, packaging metadata, console entrypoint, versioning, etc.).

---

## Project goal

Build **cmdstash**: a local CLI that lets a user stash terminal commands with metadata (AI-enriched description/tags/examples) into a local SQLite database and retrieve them quickly via search.

Primary command names (v1):
- `cmdstash add "<command>"`
- `cmdstash find "<text>"`
- `cmdstash tags`  (prints available tags)

---

## Non-goals (for now)

- No cloud sync
- No web UI
- No auth
- No telemetry
- No heavy frameworks/ORMs unless explicitly chosen later
- No executing arbitrary user-provided commands (store/recall only)

---

## Required tooling (do not substitute)

Use these exact tools unless the repo explicitly changes direction:

- **Python**: 3.14 (project pinned)
- **Package management + running**: `uv`
- **CLI framework**: `cyclopts`
- **Terminal UI (color/formatting)**: `rich`
- **Linting/formatting**: `ruff`
- **Tests**: `pytest` + `pytest-cov`
- **Database**: SQLite (prefer stdlib `sqlite3`; keep it simple)
- Default DB location
  - Use `platformdirs` to choose a per-user data directory and store the SQLite DB there by default.

---

## Canonical commands (how to work in this repo)

### Python version
- Install Python (if needed): `uv python install 3.14`
- Pin project Python: `uv python pin 3.14`
- Verify: `uv run python -V`

### Dependencies
- Add runtime deps: `uv add <package>`
- Add dev deps: `uv add --dev <package>`
- Sync environment: `uv sync`

### Run the CLI (during development)
- Help: `uv run cmdstash --help`
- Example: `uv run cmdstash add "echo hello"`

### Lint/format/test (run these often)
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
- Tests: `uv run pytest -q`
- Coverage (optional): `uv run pytest --cov=cmdstash --cov-report=term-missing`

### Makefile shortcuts
- List targets: `make help`
- Test: `make test`
- Check all: `make check`

---

## PyPI / packaging requirements (IMPORTANT)

This project should be structured to publish cleanly to PyPI:

- Use **src-layout**: package code lives under `src/cmdstash/`
- Keep packaging metadata in `pyproject.toml`
- Provide a console script entrypoint so users can run `cmdstash` after install
- Ensure `uv build` works (when build config is added)
- Keep dependencies minimal and explicit
- Follow semantic versioning (even for early releases)

Prefer packaging choices compatible with standard tooling (PEP 621 metadata in `pyproject.toml`).

---

## Repo conventions

### Code layout
Prefer a simple, testable structure:
- Code readability over clever design
- `src/cmdstash/` for library/app code
- a small CLI entry module (e.g., `src/cmdstash/cli.py`)
- keep DB access isolated (e.g., `src/cmdstash/storage/`)

Avoid sprawling modules. Keep boundaries obvious:
- CLI parsing / commands
- services/business logic
- storage (SQLite)

### Output tone
CLI output should be **polished and colorful** using Rich.
“Clever with pizazz” is good; avoid overly cute.

---

## Agent workflow rules (IMPORTANT)

### 1) Small, incremental steps only
This is a learning repo. Work must be broken into **small commits** and **small diffs**.

A good step:
- introduces one concept
- changes only a few files
- leaves the project in a working state

Avoid:
- big refactors
- sweeping rewrites
- adding many features at once

### 2) Explain intent deeply
For each step/PR-sized change, include:
- **What** you changed
- **Why** you changed it
- **How** to verify it (exact commands)

If you introduce a new pattern (e.g., FTS search, schema migrations, config dirs),
add a brief explanation in docs (or in-code docstrings/comments) describing it.

### 3) Keep planning docs current
Before implementing a chunk of work:
- update `docs/plans.md` with the relevant step status/scope
- update `docs/spec.md` if behavior or requirements change

Then implement only the scoped step.

### 4) Always keep the repo runnable
After each step, ensure:
- `uv run ruff check .` passes
- `uv run ruff format .` applied
- `uv run pytest -q` passes

### 5) Prefer simple, testable design
- Keep business logic separate from CLI wiring.
- Avoid hidden side effects; use explicit inputs (e.g., pass db path/config).
- Add minimal tests early (smoke tests are fine at first), expand gradually.
- Keep code DRY when it meaningfully improves clarity.
- Do not over-abstract for small tests or simple flows; explicit local helpers are often clearer.
- Prefer well-named functions/fixtures and light documentation over clever indirection.
- Maintain a balanced test mix across unit, integration, e2e, and smoke over time.
- Use appropriate pytest markers where they improve test selection and clarity.

### 5) Consult appropriate docs
- When writing Python code/tests/config consult @Docs pytest, @Docs ruff, @Docs rich, @Docs cyclopts, @Docs platformdirs and follow them.
---

## Documentation expectations

- `README.md` is user-facing quickstart.
- `docs/spec.md` is the source-of-truth product spec.
- `docs/plans.md` is the incremental implementation plan and step tracker.
- `docs/reference/` is the "memory stash" for practical reference notes:
  - command flags you forget
  - workflow recipes
  - topic notes (e.g., build packaging, AI integration, SQLite)

If a requirement is unclear, update `docs/spec.md` rather than guessing.

---
