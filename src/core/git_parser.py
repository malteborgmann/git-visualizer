import subprocess
from datetime import datetime, timezone
from typing import List, Dict, Tuple

from src.core.models import Commit, Branch, Repository, ChangedFile


def _run_git_command(command: List[str], repo_path: str) -> str:
    """Executes a Git command in the specified repository path and returns its output."""
    try:
        result = subprocess.run(
            ["git", "-C", repo_path] + command,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",  # Important for correct character encoding
        )
        return result.stdout.strip()
    except FileNotFoundError:
        raise RuntimeError(
            "Git command not found. Please ensure Git is installed and in your PATH."
        )
    except subprocess.CalledProcessError as e:
        error_message = f"Git command failed with error: {e.stderr.strip()}"
        if (
            "not a git repository" in e.stderr.lower()
            or "fatal: Invalid gitfile format" in e.stderr.lower()
            or "detected dubious ownership in repository at" in e.stderr.lower()
        ):
            try:
                git_dir_arg = f"--git-dir={repo_path}/.git"
                work_tree_arg = f"--work-tree={repo_path}"
                base_command = ["git", git_dir_arg, work_tree_arg]

                # Test if it is a bare repo
                is_bare_check = subprocess.run(
                    base_command + ["rev-parse", "--is-bare-repository"],
                    capture_output=True,
                    text=True,
                    check=False,
                    encoding="utf-8",
                )
                if is_bare_check.stdout.strip() == "true":
                    base_command = [
                        "git",
                        f"--git-dir={repo_path}",
                    ]  # For bare repos, work-tree is not necessary

                result = subprocess.run(
                    base_command + command,
                    capture_output=True,
                    text=True,
                    check=True,
                    encoding="utf-8",
                )
                return result.stdout.strip()
            except subprocess.CalledProcessError as e2:
                error_message = f"Git command failed: {e.stderr.strip()}. Secondary attempt failed: {e2.stderr.strip()}"
                raise ValueError(
                    f"The path '{repo_path}' is not a valid Git repository or cannot be accessed. Error: {error_message}"
                )
        raise RuntimeError(error_message)


def _get_default_branch(repo_path: str) -> str:
    """Ermittelt den Namen des Default-Branches."""
    try:
        # Versuche zuerst den Default-Branch vom Remote zu bekommen
        default_branch = _run_git_command(
            ["symbolic-ref", "refs/remotes/origin/HEAD"], repo_path
        )
        return default_branch.replace("refs/remotes/origin/", "")
    except (RuntimeError, ValueError):
        try:
            # Fallback: Versuche den Default-Branch lokal zu finden
            default_branch = _run_git_command(
                ["rev-parse", "--abbrev-ref", "HEAD"], repo_path
            )
            return default_branch
        except (RuntimeError, ValueError):
            return "main"  # Fallback auf "main" wenn nichts anderes gefunden wird


def parse_commits(repo_path: str) -> Tuple[Dict[str, Commit], Dict[str, List[str]]]:
    """Parses all commits from the repository and returns a tuple of (commits, branch_commits)."""
    commits_data: Dict[str, Commit] = {}
    branch_commits: Dict[
        str, List[str]
    ] = {}  # Maps branch names to lists of commit hashes
    commit_separator = "---GIT_COMMIT_SEPARATOR---"
    field_separator = "<FIELD_SEP>"

    # %H: Hash, %an: Author name, %ae: Author email, %ct: Committer date (Unix timestamp), %B: Full commit message, %P: Parent hashes
    log_format = f"%H{field_separator}%an{field_separator}%ae{field_separator}%ct{field_separator}%B{field_separator}%P"

    raw_log_output = _run_git_command(
        ["log", "--all", f"--pretty=format:{log_format}{commit_separator}"], repo_path
    )

    if not raw_log_output:
        return {}, {}

    raw_commits = raw_log_output.split(commit_separator)

    for raw_commit_entry in raw_commits:
        if not raw_commit_entry.strip():
            continue

        parts = raw_commit_entry.strip().split(field_separator)
        if len(parts) != 6:  # Expects 6 parts based on log_format
            continue

        (
            commit_hash,
            author_name,
            author_email,
            committer_timestamp_str,
            message,
            parent_hashes_str,
        ) = parts

        # Get numstat for this specific commit
        numstat_output = _run_git_command(
            ["log", "-1", commit_hash, "--numstat", "--pretty=format:"], repo_path
        )

        lines_added = 0
        lines_deleted = 0
        changed_files = []

        numstat_lines = numstat_output.splitlines()
        for line in numstat_lines:
            line = line.strip()
            if not line:
                continue

            stat_parts = line.split("\t")
            if len(stat_parts) == 3:
                added_str, deleted_str, file_path = stat_parts
                is_binary = added_str == "-" or deleted_str == "-"

                file_lines_added = 0 if added_str == "-" else int(added_str)
                file_lines_deleted = 0 if deleted_str == "-" else int(deleted_str)

                lines_added += file_lines_added
                lines_deleted += file_lines_deleted

                changed_files.append(
                    ChangedFile(
                        path=file_path,
                        lines_added=file_lines_added,
                        lines_deleted=file_lines_deleted,
                        is_binary=is_binary,
                    )
                )

        try:
            committer_timestamp = int(committer_timestamp_str)
            commit_date = datetime.fromtimestamp(committer_timestamp, tz=timezone.utc)
        except ValueError:
            commit_date = datetime.now(timezone.utc)

        parents = parent_hashes_str.split() if parent_hashes_str else []

        commits_data[commit_hash] = Commit(
            hash=commit_hash,
            author_name=author_name.strip(),
            author_email=author_email.strip(),
            date=commit_date,
            message=message.strip(),
            lines_added=lines_added,
            lines_deleted=lines_deleted,
            parents=parents,
            changed_files=changed_files,
        )

    for branch_name in _run_git_command(
        ["branch", "--all", "--format=%(refname:short)"], repo_path
    ).splitlines():
        if "HEAD ->" in branch_name:
            continue
        branch_name = branch_name.strip()
        if not branch_name:
            continue

        branch_commits[branch_name] = _run_git_command(
            ["rev-list", branch_name], repo_path
        ).splitlines()

    return commits_data, branch_commits


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
        raw_local_branches = _run_git_command(
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
        raw_remote_branches = _run_git_command(
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


def load_repository_data(repo_path: str) -> Repository:
    """Loads all relevant data from the Git repository."""
    commits_data, branch_commits = parse_commits(repo_path)
    branches = parse_branches(repo_path, commits_data, branch_commits)

    return Repository(path=repo_path, branches=branches)
