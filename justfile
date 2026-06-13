# 5x7 Font Draw - Project commands
# Run `just` or `just help` to see available recipes

set dotenv-load

# Show available recipes
default:
    @just --list --unsorted

# Show available recipes (alias)
help:
    @just --list --unsorted

####################
# Development
####################

# Run the app
run:
    uv run python -m src.main

# Install dependencies
install:
    uv sync

# Build standalone binaries for current platform
build:
    uv run pyinstaller --onefile --windowed --name icon-draw src/main.py

# Clean build artifacts
clean:
    rm -rf dist/ build/ __pycache__/ src/__pycache__/ *.spec

# Clean everything including virtualenv
clean-all: clean
    rm -rf .venv/

####################
# Code Quality
####################

# Run linter
lint *args:
    uv run ruff check . {{args}}

# Auto-fix lint issues
lint-fix:
    uv run ruff check --fix .

# Format code
format:
    uv run ruff format .

# Check formatting without modifying
format-check:
    uv run ruff format --check .

# Type checking
typecheck:
    uv run mypy src/ --strict

####################
# Workflows
####################

# Composite: code quality only (no tests)
check: format-check lint

# Pre-commit checks (fast, non-mutating)
pre-commit: format-check lint typecheck
    @echo "Pre-commit checks passed"
