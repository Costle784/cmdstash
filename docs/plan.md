## Current Step

### Step 2 — Developer ergonomics and memory docs pattern

### Why this step now
- Tightens day-to-day workflow with a canonical `Makefile` command surface.
- Captures useful pytest reminders in a durable, organized docs location.
- Establishes a repeatable "knowledge stash" pattern for future topics (build packaging, AI integration, SQLite).

### Scope
- Update `AGENTS.md` to reflect current tooling and workflow:
  - include `pytest-cov` in testing commands
  - include `Makefile` targets as canonical shortcuts
  - define where "reference/memory" docs live
- Extend `Makefile` with practical local development targets.
- Add a new docs section for reusable references and start it with pytest guidance.
- Add placeholders for upcoming references (build packaging, AI integration, SQLite).

### Acceptance Criteria
- `AGENTS.md` reflects actual repo conventions and test tooling.
- `make help` shows available targets and target descriptions are accurate.
- A contributor can find pytest "I always forget this flag" info under a stable docs path.
- `uv run ruff format .`, `uv run ruff check .`, and `uv run pytest -q` pass.

### Verification Commands
- `make help`
- `make check`
- `uv run ruff format .`
- `uv run ruff check .`
- `uv run pytest -q`
