"""
Data model definitions for Git repository analysis.

This module defines structured representations of Git objects such as commits,
branches, and repositories. It uses Python dataclasses to simplify object construction
and comparison. These models serve as the core data structures for Git analysis
and visualization tools.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ChangedFile:
    """
    Represents a file that was modified in a Git commit.

    Attributes:
        path (str): The file path relative to the repository root.
        lines_added (int): Number of lines added in the file.
        lines_deleted (int): Number of lines removed from the file.
        is_binary (bool): Whether the file is binary.

    """

    path: str
    lines_added: int
    lines_deleted: int
    is_binary: bool = False


@dataclass
class Commit:
    """
    Represents a single Git commit.

    Attributes:
        hash (str): The commit SHA hash.
        author_name (str): Name of the commit author.
        author_email (str): Email address of the author.
        date (datetime): Commit timestamp.
        message (str): The commit message.
        lines_added (int): Total lines added in the commit.
        lines_deleted (int): Total lines deleted in the commit.
        parents (List[str]): List of parent commit hashes (for merges).
        changed_files (List[ChangedFile]): List of files modified in the commit.

    """

    hash: str
    author_name: str
    author_email: str
    date: datetime
    message: str
    lines_added: int
    lines_deleted: int
    parents: list[str]
    changed_files: list[ChangedFile] = field(default_factory=list)


@dataclass
class Branch:
    """
    Represents a Git branch.

    Attributes:
        name (str): The name of the branch.
        head_commit_hash (str): Hash of the current HEAD commit.
        is_remote (bool): Whether the branch is a remote-tracking branch.
        is_default (bool): Whether this is the default branch (e.g., 'main' or 'master').
        category (str): Optional category assigned to the branch (e.g., "feature", "bugfix").
        commits (Dict[str, Commit]): All commits in the branch, keyed by hash.
        user_commits (Dict[str, int]): Number of commits per user.
        day_commits (Dict[str, int]): Number of commits per day (date as string).

    """

    name: str
    head_commit_hash: str
    is_remote: bool
    is_default: bool = False
    category: str = None
    commits: dict[str, Commit] = field(default_factory=dict)
    user_commits: dict[str, int] = field(default_factory=dict)
    day_commits: dict[str, int] = field(default_factory=dict)


@dataclass
class Repository:
    """
    Represents a Git repository.

    Attributes:
        path (str): Filesystem path to the root of the repository.
        branches (Dict[str, Branch]): All branches in the repository.
        loc (int): Total lines of code (used for metrics).
        ignored (int): Number of files excluded from analysis.
        total_files (int): Total number of files in the repository.
        hooks (List[str]): List of Git hooks detected in the repository.

    """

    path: str
    branches: dict[str, Branch] = field(default_factory=dict)

    loc: int = 0
    ignored: int = 0
    total_files: int = 0

    hooks: list[str] = field(default_factory=list)

    def get_default_branch(self) -> Branch | None:
        # TODO: Das hier evtl umändern und den default Branch als Attribut hier speichern
        """
        Return the default branch, if one is marked.

        Returns:
            Branch | None: The default branch object, or None if not found.

        """
        for branch in self.branches.values():
            if branch.is_default:
                return branch
        return None
