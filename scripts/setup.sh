#!/usr/bin/env bash
# Development setup script

set -e

echo "🔧 Setting up devscope development environment..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.local/bin/env
fi

# Install dependencies
echo "📦 Installing dependencies..."
uv sync --all-extras

echo "✨ Running quality checks..."

# Format code
echo "  → Formatting with ruff..."
uv run ruff format .

# Lint code
echo "  → Linting with ruff..."
uv run ruff check . --fix

# Type check
echo "  → Type checking with mypy..."
uv run mypy src/devscope

# Run tests
echo "  → Running tests..."
uv run pytest

echo "✅ Development environment ready!"
echo ""
echo "To install devscope locally:"
echo "  uv pip install -e ."
echo ""
echo "To run devscope:"
echo "  uv run devscope scan"
