# cmdstash Incremental Build Plan (No-Code Roadmap)

This is the step-by-step implementation roadmap for building `cmdstash` as a learning-first project that ships to PyPI.

## Ground Rules for Every Step

For each step below:
- Keep diffs small and focused on one concept.
- Explain **what**, **why**, and **how to verify** in the PR/commit notes.
- Do not execute a step unless the user explicitly asks to start that specific step.
- Run:
  - `uv run ruff format .`
  - `uv run ruff check .`
  - `uv run pytest -q`
- Do not start the next step until the current step meets acceptance criteria.

---

## Step 1 — Project foundation and packaging skeleton

**Goal:** Create a clean, publish-ready Python project baseline (src layout + tooling).

**Scope:**
- Establish `src/cmdstash/` package layout.
- Add/update `pyproject.toml` for PEP 621 metadata and console entrypoint (`cmdstash`).
- Ensure Python pin is `3.14`, and required baseline deps are declared:
  - runtime: `cyclopts`, `rich`, `platformdirs`
  - dev: `pytest`, `ruff`
- Add minimal package version strategy (single source of truth).

**Acceptance criteria:**
- `uv run cmdstash --help` works through the configured entrypoint.
- `uv run python -V` shows Python 3.14 in project context.
- Lint/format/tests pass (tests can be minimal at this point).

**Verify:**
- `uv sync`
- `uv run python -V`
- `uv run cmdstash --help`
- `uv run ruff format . && uv run ruff check . && uv run pytest -q`

---

## Step 2 — CLI skeleton with command groups (no persistence yet)

**Status:** Completed

**Goal:** Wire the command surface for v1 (`add`, `find`, `tags`) with polished Rich output stubs.

**Scope:**
- Implement CLI command definitions using `cyclopts`.
- Add basic Rich console setup and consistent message style.
- `cmdstash add "<command>"`, `cmdstash find "<text>"`, and `cmdstash tags` return informative placeholder output.

**Acceptance criteria:**
- All three commands are callable and display clean, professional output.
- Argument parsing errors are clear and helpful.
- No database or LLM calls yet.

**Verify:**
- `uv run cmdstash add "echo hello"`
- `uv run cmdstash find "git"`
- `uv run cmdstash tags`
- `uv run ruff format . && uv run ruff check . && uv run pytest -q`

---

## Step 3 — Configuration and default storage location

**Status:** Completed

**Goal:** Decide and implement default DB file path using `platformdirs`.

**Scope:**
- Add a small config module that resolves app data directory and DB path.
- Ensure directories are created safely when needed.
- Expose resolved path information through a diagnostics command (`cmdstash doctor`).
- Document the chosen path behavior in `README.md` or `docs/spec.md`.

**Acceptance criteria:**
- App can compute and print/log the resolved DB path in a deterministic way.
- Path behavior is test-covered (at least unit tests for resolver logic).

**Verify:**
- `uv run pytest -q`
- `uv run ruff format . && uv run ruff check .`

---

## Step 4 — SQLite schema and initialization

**Goal:** Introduce durable storage with a minimal, testable schema.

**Scope:**
- Add storage layer module(s) isolated from CLI wiring.
- Create schema for entries and tags (or chosen equivalent) with indexes.
- Add DB initialization/bootstrap path on first use.

**Acceptance criteria:**
- Schema creates successfully on empty DB.
- Re-running initialization is safe (idempotent).
- Unit tests cover schema initialization behavior.

**Verify:**
- `uv run pytest -q`
- `uv run ruff format . && uv run ruff check .`

---

## Step 5 — Tag taxonomy and `cmdstash tags`

**Goal:** Finalize MVP tag taxonomy and make `tags` command fully real.

**Scope:**
- Define initial allowed taxonomy in one explicit source (module/data file).
- Implement `cmdstash tags` to display stable ordering via Rich.
- Add tests for taxonomy integrity and command output basics.

**Acceptance criteria:**
- `cmdstash tags` always prints stable, deterministic tag list.
- Taxonomy is documented in `docs/spec.md`.

**Verify:**
- `uv run cmdstash tags`
- `uv run pytest -q`
- `uv run ruff format . && uv run ruff check .`

---

## Step 6 — LLM contract and validation layer (provider-agnostic)

**Goal:** Define strict enrichment schema before integrating any real provider.

**Scope:**
- Add data structures for enrichment result: `tags`, `description`, `examples`.
- Implement validation rules from spec:
  - tags subset of taxonomy
  - one-sentence concise description
  - 1–2 examples
- Create a provider interface abstraction that can be mocked.

**Acceptance criteria:**
- Invalid LLM-shaped outputs are rejected with actionable errors.
- Unit tests cover both valid and invalid payloads.

**Verify:**
- `uv run pytest -q`
- `uv run ruff format . && uv run ruff check .`

---

## Step 7 — `cmdstash add` with mocked enrichment and upsert behavior

**Goal:** Make `add` end-to-end with storage + normalization + upsert semantics.

**Scope:**
- Implement command normalization rules from spec.
- Connect `add` flow: parse -> enrich (mock/fake provider in tests) -> validate -> store.
- Implement duplicate handling as update/upsert with `updated_at` refresh.
- Rich success summary output for stashed entry.

**Acceptance criteria:**
- New command inserts entry + tags + examples.
- Re-adding normalized-equivalent command updates existing entry.
- LLM/storage failures show clear error and do not partially write data.

**Verify:**
- `uv run cmdstash add "echo hello"`
- `uv run cmdstash add "  echo   hello  "`
- `uv run pytest -q`
- `uv run ruff format . && uv run ruff check .`

---

## Step 8 — `cmdstash find` baseline search

**Goal:** Implement fast-enough MVP search across command/description/tags.

**Scope:**
- Add repository/query logic for text search.
- Match against command text, description, and tags.
- Return structured result rows for presentation layer.

**Acceptance criteria:**
- Query returns expected matches for each searchable field.
- Basic indexes exist for acceptable local performance.
- Tests cover common and edge-case searches.

**Verify:**
- `uv run cmdstash find "echo"`
- `uv run cmdstash find "docker"`
- `uv run pytest -q`
- `uv run ruff format . && uv run ruff check .`

---

## Step 9 — Facets and polished `find` output

**Goal:** Upgrade search UX with summary header, top tag facets, and clean result tables.

**Scope:**
- Add facet aggregation (top tags capped at 9).
- Implement result rendering with truncation rules and consistent Rich styling.
- Keep logic/presentation separated for testability.

**Acceptance criteria:**
- Output includes query summary, total count, facets, and result rows.
- Facet counts are correct for matched result sets.
- Output remains readable for long commands/descriptions.

**Verify:**
- `uv run cmdstash find "git"`
- `uv run pytest -q`
- `uv run ruff format . && uv run ruff check .`

---

## Step 10 — Real LLM provider integration behind interface

**Goal:** Replace mock path with a real provider implementation while preserving testability.

**Scope:**
- Implement provider adapter behind the existing abstraction.
- Add configuration for API key/environment handling.
- Keep tests offline by default with provider mocking/fakes.

**Acceptance criteria:**
- Real provider can be enabled in local dev when credentials exist.
- Missing/invalid provider config yields clear, actionable errors.
- Test suite remains deterministic without network calls.

**Verify:**
- `uv run pytest -q`
- `uv run ruff format . && uv run ruff check .`
- (Optional manual check) `uv run cmdstash add "<real command>"`

---

## Step 11 — Packaging hardening and release readiness

**Goal:** Ensure the project builds and installs cleanly as a PyPI package.

**Scope:**
- Finalize metadata fields in `pyproject.toml`.
- Confirm console script entrypoint and dependency declarations are correct.
- Validate source distribution/wheel build.

**Acceptance criteria:**
- `uv build` succeeds.
- Built package installs and `cmdstash --help` runs from installed artifact.
- Versioning strategy is documented.

**Verify:**
- `uv build`
- `uv run cmdstash --help`
- `uv run pytest -q`
- `uv run ruff format . && uv run ruff check .`

---

## Step 12 — Docs polish and MVP sign-off

**Goal:** Align docs with actual behavior and prepare for iterative post-MVP work.

**Scope:**
- Update `README.md` quickstart to match real commands/output.
- Update `docs/spec.md` for any clarified decisions made during implementation.
- Check off completed steps in this plan and list next-step backlog.

**Acceptance criteria:**
- A new contributor can install, run, add, find, and list tags from docs alone.
- Remaining open questions are explicit and prioritized.

**Verify:**
- Follow README from scratch on a clean environment.
- `uv run ruff format . && uv run ruff check . && uv run pytest -q`

---

## Open Decisions to Resolve Early

- Initial tag taxonomy contents (actual list of allowed tags).
- Whether FTS5 is included in MVP or scheduled immediately post-MVP.
- Whether to add `cmdstash show <id>` in MVP or defer.
- Real LLM provider choice and configuration contract.

