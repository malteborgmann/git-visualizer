from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict


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


@dataclass
class Repository:
    path: str
    branches: Dict[str, Branch] = field(default_factory=dict)

    loc: int = 0
    ignored_matched: List[str] = field(default_factory=list)
    ignored_pattern: List[str] = field(default_factory=list)
    total_files: List[str] =  field(default_factory=list)
    hooks: List[str] = field(default_factory=list)

    def get_default_branch(self) -> Branch:
        """Gibt den Default-Branch zurück."""
        for branch in self.branches.values():
            if branch.is_default:
                return branch
        return None
