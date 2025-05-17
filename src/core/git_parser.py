import subprocess
from datetime import datetime, timezone
from typing import List, Dict, Tuple

from src.core.models import Commit, Branch, Repository, ChangedFile
from src.core.git_branch_parser import parse_branches
from src.core.git_commit_parser import parse_commits
from src.core.git_stats import get_repo_stats


def load_repository_data(repo_path: str) -> Repository:
    """Loads all relevant data from the Git repository."""
    commits_data, branch_commits = parse_commits(repo_path)
    branches = parse_branches(repo_path, commits_data, branch_commits)

    total_files, ignored_matched, ignored_pattern, hooks, loc = get_repo_stats(repo_path)

    return Repository(
        path=repo_path,
        branches=branches,
        loc=loc,
        ignored_matched=ignored_matched,
        ignored_pattern=ignored_pattern,
        total_files=total_files,
        hooks=hooks,
    )
