"""
Git repository loader.

This module provides a single entry point for parsing and aggregating all
repository data—commits, branches, statistics, and hooks—into a unified
Repository object used throughout the application.
"""
from src.core.git_branch_parser import parse_branches
from src.core.git_commit_parser import parse_commits
from src.core.git_stats import get_repo_stats
from src.core.models import Repository


def load_repository_data(repo_path: str) -> Repository:
    """
    Load all Git repository data into a Repository object.

    This function collects commits, branch mappings, repository statistics, and hook information
    for a given Git repository path. It uses helper functions to parse commits and branches
    and compute repository-level statistics.

    Args:
        repo_path (str): The path to the root directory of the Git repository.

    Returns:
        Repository: A fully constructed Repository object containing all parsed metadata.

    """
    commits_data, branch_commits = parse_commits(repo_path)
    branches = parse_branches(repo_path, commits_data, branch_commits)

    total_files, ignored_count, loc, hooks = get_repo_stats(repo_path)

    return Repository(
        path=repo_path,
        branches=branches,
        loc=loc,
        ignored=ignored_count,
        total_files=total_files,
        hooks=hooks,
    )
