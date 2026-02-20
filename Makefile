.PHONY: help test test-all test-cov cov-html lint format check

help: ## Show available make targets
	@awk 'BEGIN {FS = ":.*##"; printf "\nTargets:\n"} /^[a-zA-Z0-9_-]+:.*##/ {printf "  %-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

test: ## Run fast tests (skip slow + integration)
	uv run pytest -q -m "not integration and not slow"

test-all: ## Run all tests, including slow/integration
	uv run pytest -q

test-cov: ## Run tests with coverage summary
	uv run pytest -q --cov=cmdstash --cov-report=term-missing

cov-html: ## Generate HTML coverage report
	uv run pytest -q --cov=cmdstash --cov-report=html

lint: ## Run Ruff lint checks
	uv run ruff check .

format: ## Format code with Ruff
	uv run ruff format .

check: ## Format, lint, and run tests
	$(MAKE) format
	$(MAKE) lint
	$(MAKE) test-all