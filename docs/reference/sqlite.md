# SQLite Notes

Working notes for local database design, migrations, and performance checks.

## Current project decisions

- Use stdlib `sqlite3` (no ORM in MVP).
- Use forward-only migrations tracked in `schema_migrations`.
- Use normalized command metadata tables:
  - `commands`
  - `tags`
  - `command_tags`
  - `command_examples`
- Enable foreign key enforcement per connection with `PRAGMA foreign_keys = ON`.

## Migration strategy (conventional + simple)

- Migration state is tracked in `schema_migrations`:
  - `version` (primary key)
  - `description`
  - `applied_at`
- Migrations are declared in order in code and applied sequentially.
- Each migration runs in a transaction (`with connection:` block).
- Migrations are idempotent where practical (`CREATE TABLE IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS`).

### Why this over `PRAGMA user_version`?

- `PRAGMA user_version` stores one integer only.
- `schema_migrations` gives explicit history and aligns with common tools like Alembic/Flyway patterns.

## Indexing: when to index, when not to

### Useful default rules

- Index columns used frequently in:
  - `WHERE`
  - `JOIN` conditions
  - `ORDER BY` / grouping paths used often
- Avoid indexing everything; each index adds write cost and storage cost.
- Add indexes after confirming a query pattern is real and frequent.

### Indexes already provided by constraints

- `PRIMARY KEY` columns are indexed.
- `UNIQUE` columns are indexed.
- Composite `PRIMARY KEY (a, b)` supports lookups starting with `a` (leftmost-prefix behavior).

### Composite key vs surrogate integer key

For join tables like `command_tags`, there are two common designs:

1) Composite primary key:
- `PRIMARY KEY(command_id, tag_id)`
- No extra `id` column

2) Surrogate key + unique pair:
- `id INTEGER PRIMARY KEY`
- `UNIQUE(command_id, tag_id)`

When to prefer composite key (our current choice):
- The row's identity is naturally "this command + this tag".
- You do not need to reference this join row by its own ID from other tables.
- You want a smaller, simpler schema with one fewer column/index.

When to prefer surrogate integer key:
- Other tables need to point to a specific join row (rare for simple many-to-many tables).
- You expect app code or APIs to address join rows directly by ID.
- You want a stable single-column key for external references.

Rule of thumb:
- For pure many-to-many link tables, prefer composite primary key.
- Add a surrogate `id` only when there is a concrete need for row-level identity.

### Leftmost-prefix behavior (clear example)

Given:
- `PRIMARY KEY(command_id, tag_id)` on `command_tags`

This index can efficiently serve queries that start with `command_id`, such as:

```sql
SELECT tag_id
FROM command_tags
WHERE command_id = ?;
```

It generally does not efficiently serve queries that only filter by `tag_id`, such as:

```sql
SELECT command_id
FROM command_tags
WHERE tag_id = ?;
```

That is why we add a second index for the reverse direction:
- `CREATE INDEX ... ON command_tags(tag_id)`

Mental model:
- Think of the composite index as sorted by `(command_id, then tag_id)`.
- Fast lookups need to start from the first sort key (`command_id`).

### Current rationale in cmdstash

- `commands.command` is `UNIQUE`, so no extra index needed.
- `tags.name` is `UNIQUE`, so no extra index needed.
- `command_tags` has `PRIMARY KEY(command_id, tag_id)`:
  - Good for `command_id -> tags` lookups.
  - Add a separate index on `tag_id` for `tag -> commands` queries and facets.
- `command_examples` has `UNIQUE(command_id, position)`, which already helps common per-command example fetches.

## Query profiling workflow (developer practical)

### 1) Inspect query plan first

In SQLite shell:

```sql
EXPLAIN QUERY PLAN
SELECT c.id, c.command
FROM commands c
JOIN command_tags ct ON ct.command_id = c.id
JOIN tags t ON t.id = ct.tag_id
WHERE t.name = 'docker';
```

Look for:
- `SCAN` = full table scan (sometimes okay for tiny tables)
- `SEARCH ... USING INDEX` = index use

### 2) Time the query

In `sqlite3` CLI:

```sql
.timer on
SELECT ...;
```

Run multiple times:
- first run includes cache misses
- later runs show warm-cache behavior

`sqlite_profile_demo.py` reports both average (`avg`) and p95 latency:
- `avg`: arithmetic mean across runs.
- `p95`: 95th percentile; about 95% of runs are at or below this value.

Why p95 matters:
- Averages can hide occasional slow runs.
- p95 is a better "tail latency" signal for user-perceived consistency.
- For tiny sample sizes, p95 is approximate; use more runs (for example 20-100) for stability.

### 3) Get realistic data volume

- Performance checks on 20 rows are misleading.
- Seed enough records to match expected user scale (for example: 1k, 10k, 50k commands).

### 4) Re-check plan after index change

- Add one index.
- Re-run `EXPLAIN QUERY PLAN` and timing.
- Keep the index only if there is clear benefit.

## Useful SQLite internals (developer-level)

- B-tree indexes back most lookups; index choice determines scan shape.
- SQLite optimizer is cost-based but lightweight; statistics help.
- `ANALYZE` updates planner stats for better decisions on larger datasets.
- `PRAGMA optimize` can apply lightweight planner/index maintenance.
- Foreign keys are connection-local in SQLite; always enable them on connect.

## Parameterized SQL and injection safety

### What to do

- Always send SQL text and values separately.
- In Python `sqlite3`, use `?` placeholders and pass a tuple/list of values.

Good:

```python
connection.execute(
    "INSERT INTO tags(name) VALUES (?)",
    (tag_name,),
)
```

Bad (unsafe string interpolation):

```python
connection.execute(f"INSERT INTO tags(name) VALUES ('{tag_name}')")
```

### Why parameterization helps

- The SQL statement is parsed as SQL.
- Parameters are bound as data values, not executable SQL.
- User input containing quotes or SQL tokens is treated as literal text.
- This blocks classic SQL injection payloads from changing query structure.

### Important boundaries

- Parameterization protects values, not SQL identifiers.
  - You cannot parameterize table names or column names with `?`.
  - If identifiers are dynamic, use a strict allowlist and map to known safe strings.
- It does not replace app-level authorization checks.
- It does not fix logic bugs such as "query too broad" mistakes.

### Practical checklist

- Never build SQL by concatenating user input into query text.
- Use placeholders for every external value in `INSERT`, `UPDATE`, `DELETE`, and `WHERE` clauses.
- Keep dynamic SQL pieces limited to allowlisted identifier maps.
- Add tests with hostile-looking input (quotes, semicolons, SQL keywords) to verify behavior.

## Speed testing options

### Lightweight (built-in)

- Use `sqlite3` CLI + `.timer on` + `EXPLAIN QUERY PLAN`.
- Add repeatable benchmark scripts under `tests/` or `scripts/`.
- Use `scripts/sqlite_profile_demo.py` to seed data, print query plans/timings,
  and run before/after index experiments (exact match + LIKE prefix).

### Python test-level

- Add focused performance tests that create fixture datasets and time target queries.
- Optional tooling:
  - `pytest-benchmark` (nice historical comparisons)
  - `pytest` markers for opt-in perf tests (avoid slowing default suite)

## Tooling recommendations

### CLI tools

- `sqlite3` (canonical and always available)
- `litecli` (autocompletion + nicer CLI UX)
- `ripgrep` + source inspection for query callsites in code

### GUI tools

- DB Browser for SQLite (simple, free, easy table/index browsing)
- TablePlus (polished, lightweight)
- DBeaver (heavier but powerful and free community edition)

## Handy command snippets

Open project DB:

```bash
sqlite3 ~/Library/Application\ Support/cmdstash/cmdstash.db
```

Run the demo profiler script:

```bash
uv run python scripts/sqlite_profile_demo.py --commands 10000 --runs 7
```

Run with more stable percentile samples:

```bash
uv run python scripts/sqlite_profile_demo.py --commands 10000 --runs 30
```

Run the same script but skip the before/after index experiment:

```bash
uv run python scripts/sqlite_profile_demo.py --commands 10000 --runs 7 --skip-index-experiment
```

Inspect tables/indexes:

```sql
.tables
.schema commands
.indexes command_tags
```

Quick migration history check:

```sql
SELECT version, description, applied_at
FROM schema_migrations
ORDER BY version;
```

## Guardrails

- Keep SQL in storage layer, not CLI wiring.
- Favor simple readably-named queries before clever SQL.
- Measure before adding indexes.
- Document each new index with the query pattern it is intended to accelerate.
