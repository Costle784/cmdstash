# SQLite Notes

Working notes for local database design and operations.

## To Capture

- Final DB file location via `platformdirs`
- Schema decisions (`entries`, `tags`, indexes)
- Migration strategy (if/when introduced)
- Search approach (basic indexes vs FTS5)

## Debug Commands (to fill in as schema lands)

- Open DB shell
- Inspect schema
- Run basic query checks

## Guardrails

- Keep storage layer isolated from CLI wiring.
- Prefer simple `sqlite3` patterns first.
