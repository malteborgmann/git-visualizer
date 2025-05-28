"""
Commit statistics utilities for Git branches.

Provides helper function for analyzing commit activity
Counts commits per user for a given Git branch.
"""

from src.core.models import Branch


def get_commits_per_user(branch: Branch) -> dict[str, int]:
    """
    Count the number of commits made by each user in a Git branch.

    Args:
        branch (Branch): A Branch object containing commit data.

    Returns:
        Dict[str, int]: A dictionary mapping user names to their number of commits.

    """
    user_commits = {}
    for commit in branch.commits.values():
        if commit.author_name not in user_commits:
            user_commits[commit.author_name] = 0
        user_commits[commit.author_name] += 1
    return user_commits
