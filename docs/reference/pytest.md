# Pytest Quick Reference

## Common Pytest Flags

- `-q` quiet mode (less output noise)
- `-ra` extra end-of-run summary for all outcomes except passes
- `-m "<expr>"` run tests matching marker expression
- `-k "<expr>"` run tests by name substring/expression
- `-x` stop at first failure
- `-s` show `stdout`/`stderr` output
- `--lf` run only last failed tests
- `--ff` run failed tests first
- `--maxfail=<n>` stop after `n` failures

## `-r` / `-ra` quick reference

- `-r <chars>` controls what appears in the short test summary at the end.
- `-ra` is shorthand for "all except passes" (helpful default signal without lots of noise).
- Common letters:
  - `f` failed
  - `E` error
  - `s` skipped
  - `x` xfailed
  - `X` xpassed
  - `p` passed
  - `P` passed with output
- Useful combos:
  - `-ra` broad summary without pass spam
  - `-rfE` only failures + errors
  - `-rA` everything (including passes)

## Marker Examples

- Skip slow: `-m "not slow"`
- Skip integration: `-m "not integration"`
- Unit only: `-m "unit"`
- Fast local default: `-m "not integration and not slow"`

## Test Types (Quick Guide)

- `unit` - tests one function/class in isolation (fast, mocked dependencies).  
  Run: local on every save/commit, and in every PR CI run.

- `integration` - tests multiple components together (e.g., app + SQLite).  
  Run: local before opening PR, and in every PR CI run.

- `smoke` - minimal critical-path checks proving the app starts and core flow works.  
  Run: always in PR CI and post-deploy checks; also useful locally after setup changes.

- `e2e` - full user flow through real boundaries (CLI entrypoint, filesystem, services).  
  Run: CI on merge-to-main and/or scheduled/nightly (can be slower/flakier).

- `regression` - targeted test added for a bug so it never returns.  
  Run: wherever its parent type runs (usually PR CI + local when touching that area).

Practical default:
- Keep `unit` + lightweight `smoke` in the fast path.
- Gate PRs with `unit` + `integration` + smoke coverage.
- Run heavier `e2e` on main/nightly unless your suite is very fast.

## Coverage Notes

Current defaults in `pytest.ini`:
- `--cov=cmdstash`
- `--cov-report=html`
- `--cov-report=term-missing`
- `--cov-fail-under=85`

Useful overrides:
- Disable fail-under temporarily: `--cov-fail-under=0`
- Skip HTML report for speed: `--cov-report=term-missing`

## `pytest-cov` quick hits

- `pytest-cov` is a separate plugin package; `pytest` does not include `--cov` flags by default.
- If `--cov` is "unrecognized arguments", the plugin is missing from the environment.
- Use terminal coverage (`term`/`term-missing`) for fast local feedback.
- Use HTML coverage when you want to inspect missed lines interactively.
- In CI, prefer machine-readable reports (commonly XML) plus a concise terminal summary.
- Keep one source of truth for thresholds (`--cov-fail-under`) so local and CI expectations stay aligned.

## Quick gotchas

- Marker expressions need quotes in most shells.
- `-k` matches test names, class names, and file substrings; it is broader than many people expect.
- `--lf` can show "no tests ran" if no prior failures were recorded in cache.
- `-x` and `--maxfail=1` are effectively equivalent in most workflows.

## Config locations

- Pytest config: `pytest.ini`
