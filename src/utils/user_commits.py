from typing import Dict
from src.core.models import Branch, Commit

def get_commits_per_user(branch: Branch) -> Dict[str, int]:
    """
    Gibt die Anzahl der Commits pro User zurück.
    """
    user_commits = {}
    for commit in branch.commits.values():
        if commit.author_name not in user_commits:
            user_commits[commit.author_name] = 0
        user_commits[commit.author_name] += 1
    return user_commits