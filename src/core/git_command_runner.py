"""Utilities for executing Git commands within a repository."""

from __future__ import annotations

from pathlib import Path
import subprocess


def run_git_command(command: list[str], repo_path: str | Path) -> str:
    """Run a Git command inside the given repository path and return the output."""
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, *command],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )
        return result.stdout.strip()
    except FileNotFoundError:
        msg = "Git is not installed or not in PATH."
        raise RuntimeError(msg)
    except subprocess.CalledProcessError as err:
        msg = f"Git command failed: {err.stderr.strip()}"
        raise RuntimeError(msg)
