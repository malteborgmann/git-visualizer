from src.core.git_command_runner import run_git_command
from src.core.models import Branch, Commit


def _get_default_branch(repo_path: str) -> str:
    """Ermittelt den Namen des Default-Branches."""
    try:
        # Versuche zuerst den Default-Branch vom Remote zu bekommen
        default_branch = run_git_command(
            ["symbolic-ref", "refs/remotes/origin/HEAD"],
            repo_path,
        )
        return default_branch.replace("refs/remotes/origin/", "")
    except (RuntimeError, ValueError):
        try:
            # Fallback: Versuche den Default-Branch lokal zu finden
            default_branch = run_git_command(
                ["rev-parse", "--abbrev-ref", "HEAD"],
                repo_path,
            )
            return default_branch
        except (RuntimeError, ValueError):
            return "main"  # Fallback auf "main" wenn nichts anderes gefunden wird


def parse_branches(
    repo_path: str, commits_data: dict[str, Commit], branch_commits: dict[str, list[str]]
) -> dict[str, Branch]:
    """Parse all local and remote branches and assigns commits to them."""
    branches_data: dict[str, Branch] = {}
    default_branch_name = _get_default_branch(repo_path)
    field_separator = "<FIELD_SEP>"

    def _assign_branch_commits(_name, _head_hash, _is_remote, _is_default):
        branch = Branch(
            name=_name,
            head_commit_hash=_head_hash,
            is_remote=_is_remote,
            is_default=_is_default,
        )
        # Add commits to branch
        if _name in branch_commits: # If name is in branches
            for commit_hash in branch_commits[_name]: # Commit is in the commit list of that branch
                if commit_hash in commits_data:
                    branch.commits[commit_hash] = commits_data[commit_hash] # Assign commit to branch
        branches_data[_name] = branch # Branch name: Branch Object

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

                _assign_branch_commits(
                    name, head_hash, False, is_default
                )
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

                _assign_branch_commits(
                    name, head_hash, True, is_default
                )

    except RuntimeError as e:
        print(f"Could not parse remote branches: {e}")  # Non-critical, maybe no remotes

    return branches_data
