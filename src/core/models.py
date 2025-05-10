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

@dataclass
class Repository:
    path: str
    commits: Dict[str, Commit] = field(default_factory=dict)
    branches: Dict[str, Branch] = field(default_factory=dict) 