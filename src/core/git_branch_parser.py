from typing import List, Dict
from src.core.models import Commit, Branch
from src.core.git_command_runner import run_git_command


def _get_default_branch(repo_path: str) -> str:
    """Ermittelt den Namen des Default-Branches."""
    try:
        # Versuche zuerst den Default-Branch vom Remote zu bekommen
        default_branch = run_git_command(
            ["symbolic-ref", "refs/remotes/origin/HEAD"], repo_path
        )
        return default_branch.replace("refs/remotes/origin/", "")
    except (RuntimeError, ValueError):
        try:
            # Fallback: Versuche den Default-Branch lokal zu finden
            default_branch = run_git_command(
                ["rev-parse", "--abbrev-ref", "HEAD"], repo_path
            )
            return default_branch
        except (RuntimeError, ValueError):
            return "main"  # Fallback auf "main" wenn nichts anderes gefunden wird


def parse_branches(
    repo_path: str,
    commits_data: Dict[str, Commit],
    branch_commits: Dict[str, List[str]],
) -> Dict[str, Branch]:
    """Parses all local and remote branches and assigns commits to them."""
    branches_data: Dict[str, Branch] = {}
    default_branch_name = _get_default_branch(repo_path)
    field_separator = "<FIELD_SEP>"

    # Local branches
    # %(refname:short) gives the short name of the branch
    # %(objectname) gives the commit hash the branch points to
    try:
        raw_local_branches = run_git_command(
            ["branch", f"--format=%(refname:short){field_separator}%(objectname)"],
            repo_path,
        )
        if raw_local_branches:
            for line in raw_local_branches.splitlines():
                if not line.strip():
                    continue
                name, head_hash = line.strip().split(field_separator)
                is_default = name == default_branch_name
                branch = Branch(
                    name=name,
                    head_commit_hash=head_hash,
                    is_remote=False,
                    is_default=is_default,
                )
                # Füge Commits zum Branch hinzu
                if name in branch_commits:
                    for commit_hash in branch_commits[name]:
                        if commit_hash in commits_data:
                            branch.commits[commit_hash] = commits_data[commit_hash]
                branches_data[name] = branch
    except RuntimeError as e:
        print(f"Could not parse local branches: {e}")  # Non-critical, maybe no branches

    # Remote branches
    try:
        raw_remote_branches = run_git_command(
            [
                "branch",
                "-r",
                f"--format=%(refname:short){field_separator}%(objectname)",
            ],
            repo_path,
        )
        if raw_remote_branches:
            for line in raw_remote_branches.splitlines():
                if not line.strip() or "HEAD ->" in line:  # Ignore HEAD -> origin/main
                    continue
                name, head_hash = line.strip().split(field_separator)
                is_default = name == f"origin/{default_branch_name}"
                branch = Branch(
                    name=name,
                    head_commit_hash=head_hash,
                    is_remote=True,
                    is_default=is_default,
                )
                # Add commits to branch
                if name in branch_commits:
                    for commit_hash in branch_commits[name]:
                        if commit_hash in commits_data:
                            branch.commits[commit_hash] = commits_data[commit_hash]
                branches_data[name] = branch
    except RuntimeError as e:
        print(f"Could not parse remote branches: {e}")  # Non-critical, maybe no remotes

    return branches_data
