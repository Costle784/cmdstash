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

## Quick gotchas

- A leading tab is required for recipe lines in Makefiles.
- Use `:=` for immediate assignment and `=` for deferred expansion.
- Prefer `$(VAR)` over `$VAR` inside Makefiles for consistency and clarity.
