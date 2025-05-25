from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class ChangedFile:
    path: str
    lines_added: int
    lines_deleted: int
    is_binary: bool = False


@dataclass
class Commit:
    hash: str
    author_name: str
    author_email: str
    date: datetime
    message: str
    lines_added: int
    lines_deleted: int
    parents: List[str]
    changed_files: List[ChangedFile] = field(default_factory=list)


@dataclass
class Branch:
    name: str
    head_commit_hash: str
    is_remote: bool
    is_default: bool = False
    category: str = None
    commits: Dict[str, Commit] = field(default_factory=dict)
    user_commits: Dict[str, int] = field(default_factory=dict)
    day_commits: Dict[datetime, int] = field(default_factory=dict)


@dataclass
class Repository:
    path: str
    branches: Dict[str, Branch] = field(default_factory=dict)

    loc: int = 0
    ignored: int = 0
    total_files: int = 0

    hooks: List[str] = field(default_factory=list)

    def get_default_branch(self) -> Branch:
        """Gibt den Default-Branch zurück."""
        for branch in self.branches.values():
            if branch.is_default:
                return branch
        return None
