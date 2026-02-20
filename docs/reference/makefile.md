# Makefile Quick Reference

## Syntax you asked about

- `$(MAKE)`  
  Use Make's own executable to run another target (recursive make).  
  Why use it: inherits make flags like `-j`, `-n`, and keeps behavior consistent.

- `@awk ...`  
  `awk` is a text-processing command; here it parses this Makefile and prints `target -> description` lines for `make help`.  
  `@` means "don't echo the command itself", only show its output.

- `.PHONY`  
  Declares targets that are commands, not files.  
  Why use it: if a file named `test` exists, `make test` still runs the test command.

## Useful commands in this repo

- `make help` - list available targets
- `make test` - fast local tests (skips slow/integration)
- `make test-all` - run full test suite
- `make test-cov` - run tests with coverage summary
- `make cov-html` - generate HTML coverage report
- `make lint` - run Ruff checks
- `make format` - run Ruff formatter
- `make check` - format + lint + full tests
