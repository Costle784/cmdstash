# cmdstash - Stop re-Googling the same commands

`cmdstash` is a CLI for saving useful terminal commands with helpful metadata,
then finding them quickly later.

This repository is being built incrementally as a learning-first project.

## Current status

Steps 1-3 are complete:

- Python 3.14 project setup
- `src/` package layout
- packaging metadata in `pyproject.toml`
- console entrypoint wired (`cmdstash`)
- CLI skeleton for `add`, `find`, and `tags` (placeholder output)
- default storage path resolution via `platformdirs`

Planned next: SQLite schema + initialization (step 4).

## Default database location

`cmdstash` resolves its default SQLite path with
`platformdirs.user_data_path("cmdstash", ensure_exists=True)` and stores the DB as
`cmdstash.db` in that directory.

## Requirements

- Python `3.14`
- `uv`

## Quickstart

```bash
uv sync
uv run python -V
uv run cmdstash --help
```

## Development workflow

Use the `Makefile` as the primary developer command surface.

Start here:

```bash
make help
```

Common targets:

- `make test` - fast local test run (skips slow/integration markers)
- `make test-all` - full test suite
- `make test-cov` - tests + terminal coverage summary
- `make cov-html` - generate HTML coverage report
- `make lint` - run Ruff checks
- `make format` - run Ruff formatter
- `make check` - format + lint + full tests

## Planned command surface (v1)

- `cmdstash add "<command>"`
- `cmdstash find "<text>"`
- `cmdstash tags`
- `cmdstash doctor`

## Diagnostics command

Use `cmdstash doctor` to print useful local runtime/configuration information, such as:

- app version
- supported Python range
- runtime Python/platform (debug context)
- resolved database path

This command is intended to grow as config surfaces are added (for example, model/provider settings).

## Reference notes (memory stash)

For practical "don't forget this" notes, see `docs/reference/`.

Current reference pages:

- `docs/reference/pytest.md`
- `docs/reference/makefile.md`
- `docs/reference/build-packaging.md`
- `docs/reference/ai-integration.md`
- `docs/reference/sqlite.md`
- `docs/reference/platformdirs.md`

## License

MIT
