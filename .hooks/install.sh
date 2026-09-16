#!/bin/bash
# Auto-install git hooks for pytest-param-table
# This script is run automatically by setup.py during development install

set -e

echo "Setting up git hooks for pytest-param-table..."

# Check if we're in a git repository
if [ ! -d .git ]; then
    echo "Not in a git repository, skipping hook installation"
    exit 0
fi

# Install pre-commit if not already installed
if ! command -v pre-commit &> /dev/null; then
    echo "Installing pre-commit..."
    pip install pre-commit
fi

# Install the pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install --install-hooks

# Install pre-push hooks
echo "Installing pre-push hooks..."
pre-commit install --hook-type pre-push

echo "✅ Git hooks installed successfully!"
echo ""
echo "Hooks installed:"
echo "  - pre-commit: Runs ruff formatting, linting, and type checking"
echo "  - pre-push: Runs full test suite"
echo ""
echo "To run manually:"
echo "  pre-commit run --all-files    # Run all pre-commit hooks"
echo "  pre-commit run --hook-stage pre-push  # Run pre-push hooks"
