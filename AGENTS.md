---
description: 
alwaysApply: true
---

# AGENTS.md — cmdstash

This is a **learning project**. Optimize for **clarity, tiny steps, and explanation** over speed.
Prioritize readability and easy review. Keep code and docs explicit.
Project target: clean **PyPI publishing** (src-layout, metadata, entrypoint, versioning).

---

## Project goal

Build **cmdstash**: a local CLI that lets a user stash terminal commands with metadata (AI-enriched description/tags/examples) into a local SQLite database and retrieve them quickly via search.

Primary v1 commands:
- `cmdstash add "<command>"`
- `cmdstash find "<text>"`
- `cmdstash tags` (prints available tags)

---

## Non-goals (for now)

- No cloud sync
- No web UI
- No auth
- No telemetry
- No heavy frameworks/ORMs unless explicitly chosen later
- No executing arbitrary user-provided commands (store/recall only)

---

## Required stack (do not substitute)

Use these unless the repo explicitly changes direction:

- **Python**: 3.14 (project pinned)
- **Package manager / runner**: `uv`
- **CLI framework**: `cyclopts`
- **Terminal UI**: `rich`
- **Linting/formatting**: `ruff`
- **Tests**: `pytest` + `pytest-cov`
- **Database**: SQLite (prefer stdlib `sqlite3`)
- **Default DB location**: use `platformdirs` per-user data dir

---

## Canonical commands

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

### Lint / format / test
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
- Tests: `uv run pytest -q`
- Coverage (optional): `uv run pytest --cov=cmdstash --cov-report=term-missing`

### Makefile shortcuts
- List targets: `make help`
- Test: `make test`
- Check all: `make check`

---

## Packaging requirements

Keep packaging PyPI-friendly:

- Use **src layout**: `src/cmdstash/`
- Keep packaging metadata in `pyproject.toml`
- Provide a console script entrypoint for `cmdstash`
- Ensure `uv build` works
- Keep dependencies minimal and explicit
- Follow semantic versioning

---

## Conventions

### Code layout
- Keep modules small and testable.
- Keep boundaries clear: CLI wiring, service logic, storage.
- Keep DB access isolated (e.g., `src/cmdstash/storage/`).

### Output tone
CLI output should be polished and colorful with Rich.
“Clever with pizazz” is fine; avoid overly cute.

---

## Agent workflow (must follow)

1. **Small steps only**
   - One concept per change; keep diffs small and working.
   - Avoid broad refactors unless explicitly requested.

2. **Explain intent clearly**
   - For each step: what changed, why, and exact verify commands.
   - If introducing new patterns, document briefly.

3. **Keep plan/spec current**
   - Update `docs/plans.md` before scoped implementation.
   - Update `docs/spec.md` when behavior/requirements change.

4. **Always leave repo runnable**
   - Run: `uv run ruff check .`, `uv run ruff format .`, `uv run pytest -q`.

5. **Prefer simple, testable design**
   - Separate business logic from CLI wiring.
   - Avoid hidden side effects; prefer explicit inputs.
   - Add minimal tests early; expand in small increments.
   - Avoid over-abstraction.

6. **Consult docs when coding**
   - Use `@Docs pytest`, `@Docs ruff`, `@Docs rich`, `@Docs cyclopts`, `@Docs platformdirs`.

7. **Output style (learning + concise)**
   - Teach the reasoning, but keep defaults concise.
   - Start with short explanation + actionable steps; expand only when complexity/risk is high or user asks.
   - Use examples sparingly and only when they improve understanding.

8. **Usage budget mode**
   - Keep responses compact and high-signal.
   - Ask at most one clarifying question when possible; otherwise proceed with safest assumption.
   - Minimize tool calls: batch reads/searches and avoid redundant re-reads.
   - Prefer small, targeted edits over broad rewrites.
   - For large tasks, propose a brief plan first and execute one slice at a time.

---

## Documentation expectations

- `README.md`: user-facing quickstart.
- `docs/spec.md` is the source-of-truth product spec.
- `docs/plans.md` is the incremental implementation plan and step tracker.
- `docs/reference/`: practical notes (flags, recipes, topic references).

If a requirement is unclear, update `docs/spec.md` rather than guessing.

---
