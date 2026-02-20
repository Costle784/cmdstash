# Build + Packaging Notes

Working notes for Python packaging and release flow.

## Core Commands

- Build artifacts: `uv build`
- Validate metadata (future): `uv run twine check dist/*`

## Reminders

- Keep metadata in `pyproject.toml` (PEP 621).
- Ensure console entrypoint for `cmdstash` remains correct.
- Keep dependencies minimal and explicit.

## To Capture As Decisions

- Version bump workflow
- Release checklist
- PyPI publish commands
