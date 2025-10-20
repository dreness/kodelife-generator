#!/usr/bin/env bash

# Format and lint script for CI and pre-commit hooks
# Runs ruff with auto-fix and black formatter

set -e  # Exit on any error

echo "Running ruff check with auto-fix..."
uv run ruff check --fix --unsafe-fixes src/ tests/ examples/ tools/

echo "Running black formatter..."
uv run black src/ tests/ examples/ tools/

echo "✓ Formatting complete!"
