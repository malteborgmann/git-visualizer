from pathlib import Path
import os
import stat
import subprocess

import pytest

from src.core.git_branch_parser import _get_default_branch, parse_branches
from src.core.git_command_runner import run_git_command
from src.core.git_commit_parser import parse_commits
from src.core.git_parser import load_repository_data
from src.core.git_stats import (
    _count_lines_of_code,
    _get_hooks,
    _get_ignored_paths,
    get_repo_stats,
)
from src.core.models import Branch, Repository


@pytest.fixture
def git_repo(tmp_path):
    """Erstellt ein temporäres Git-Repository mit:
    - main branch
    - feature/test branch
    - .gitignore und ignorierter Datei
    - Hooks-Verzeichnis mit ausführbarem Skript
    - Zwei Commits: einer auf main, einer auf feature/test
    """
    repo_path = tmp_path / "repo"
    repo_path.mkdir()

    subprocess.run(["git", "init"], cwd=repo_path, check=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"], cwd=repo_path, check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True,
    )
    subprocess.run(
        ["git", "symbolic-ref", "HEAD", "refs/heads/main"],
        cwd=repo_path,
        check=True,
    )

    (repo_path / ".gitignore").write_text("ignored.txt\n")
    subprocess.run(["git", "add", ".gitignore"], cwd=repo_path, check=True)
    (repo_path / "tracked.txt").write_text("line1\nline2\n")
    subprocess.run(["git", "add", "tracked.txt"], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True)

    subprocess.run(["git", "checkout", "-b", "feature/test"], cwd=repo_path, check=True)
    (repo_path / "feature.txt").write_text("a\nb\nc\n")
    subprocess.run(["git", "add", "feature.txt"], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", "Feature commit"], cwd=repo_path, check=True)
    subprocess.run(["git", "checkout", "main"], cwd=repo_path, check=True)

    (repo_path / "ignored.txt").write_text("ignore me")

    hooks_dir = repo_path / ".git" / "hooks"
    hook = hooks_dir / "pre-commit"
    hook.write_text("#!/bin/sh\necho pre-commit")
    hook.chmod(hook.stat().st_mode | stat.S_IXUSR)  # CHMOD +x pre-commit
    (hooks_dir / "post-commit.sample").write_text("sample")

    return str(repo_path)


def test_run_git_command_success(git_repo):
    out = run_git_command(["rev-parse", "--is-inside-work-tree"], git_repo)
    assert out.lower() == "true"


def test_default_branch(git_repo):
    assert _get_default_branch(git_repo) == "main"


def test_ignored_paths(git_repo):
    ignored = _get_ignored_paths(git_repo)
    assert "ignored.txt" in ignored
    assert all("ignored.txt" in p for p in ignored)


def test_hooks(git_repo):
    hooks = _get_hooks(git_repo)
    assert "pre-commit" in hooks
    assert all(not h.endswith(".sample") for h in hooks)


def test_count_lines_of_code(git_repo):
    # tracked.txt (2 line) + .gitignore (1 line) = 5
    assert _count_lines_of_code(git_repo) == 3


def test_repo_stats(git_repo):
    total, ignored_count, loc, hooks = get_repo_stats(git_repo)
    # tracked + .gitignore = 2
    assert total == 2
    assert ignored_count == 1
    assert loc == 3
    assert hooks == ["pre-commit"]


def test_parse_commits_and_branch_commits(git_repo):
    commits_data, branch_commits = parse_commits(git_repo)
    assert len(commits_data) == 2
    assert set(branch_commits.keys()) >= {"main", "feature/test"}


def test_parse_branches(git_repo):
    commits_data, branch_commits = parse_commits(git_repo)
    branches = parse_branches(git_repo, commits_data, branch_commits)
    assert isinstance(branches, dict)
    assert "main" in branches and "feature/test" in branches
    assert isinstance(branches["main"], Branch)
    assert len(branches["main"].commits) == 1


def test_load_repository_data(git_repo):
    repo = load_repository_data(git_repo)
    assert isinstance(repo, Repository)
    assert set(repo.branches.keys()) == {"main", "feature/test"}


def test_run_git_command_failure(tmp_path):
    fake_path = tmp_path / "not_a_repo"
    fake_path.mkdir()
    with pytest.raises(ValueError):
        run_git_command(["status"], str(fake_path))
