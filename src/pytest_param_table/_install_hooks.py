"""Auto-install git hooks for development."""

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Install pre-commit hooks for pytest-param-table development."""
    print("Setting up git hooks for pytest-param-table...")

    # Find the repository root
    current_dir = Path.cwd()
    repo_root = current_dir

    # Look for .git directory
    while repo_root != repo_root.parent:
        if (repo_root / ".git").exists():
            break
        repo_root = repo_root.parent
    else:
        print("Not in a git repository, skipping hook installation")
        return 0

    # Change to repo root
    os.chdir(repo_root)

    # Check if pre-commit is installed
    try:
        subprocess.run(
            ["pre-commit", "--version"],
            check=True,
            capture_output=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Installing pre-commit...")
        # Try uv first, fall back to pip
        try:
            subprocess.run(
                ["uv", "pip", "install", "pre-commit"],
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pre-commit"],
                check=True,
            )

    # Install the pre-commit hooks
    print("Installing pre-commit hooks...")
    subprocess.run(
        ["pre-commit", "install", "--install-hooks"],
        check=True,
    )

    # Install pre-push hooks
    print("Installing pre-push hooks...")
    subprocess.run(
        ["pre-commit", "install", "--hook-type", "pre-push"],
        check=True,
    )

    print("✅ Git hooks installed successfully!")
    print()
    print("Hooks installed:")
    print("  - pre-commit: Runs ruff formatting, linting, and type checking")
    print("  - pre-push: Runs full test suite")
    print()
    print("To run manually:")
    print("  pre-commit run --all-files              # Run all pre-commit hooks")
    print("  pre-commit run --hook-stage pre-push    # Run pre-push hooks")

    return 0


if __name__ == "__main__":
    sys.exit(main())
