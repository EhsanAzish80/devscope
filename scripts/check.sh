#!/usr/bin/env bash
# Run all quality checks

set -e

echo "🔍 Running quality checks..."

echo "  → Formatting check..."
uv run ruff format --check .

echo "  → Linting..."
uv run ruff check .

echo "  → Type checking..."
uv run mypy src/devscope

echo "  → Running tests..."
uv run pytest

echo "✅ All checks passed!"
