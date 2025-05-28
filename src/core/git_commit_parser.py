"""
Git commit and branch parser module.

This module provides utilities to extract structured commit and branch information from a Git
repository. It executes `git log`, `git rev-list`, and related commands to collect commit metadata,
file-level statistics, and branch-to-commit mappings.

The main public function is:
- `parse_commits(repo_path)`: Combines commit and branch data into structured dictionaries.

Private helper functions:
- `_get_commit_data(repo_path)`: Parses commit metadata and changed files from the full Git log.
- `_get_branch_commits(repo_path)`: Maps each Git branch to the list of commit hashes it contains.

The module depends on `run_git_command(...)` to execute Git commands safely and consistently, and
uses `Commit` and `ChangedFile` dataclasses to represent structured commit information.

Returns:
    - A dictionary of commit hashes mapped to `Commit` objects
    - A dictionary of branch names mapped to commit hash lists
"""

from datetime import datetime, timezone

from src.core.git_command_runner import run_git_command
from src.core.models import ChangedFile, Commit


def parse_commits(repo_path: str) -> (dict[str, Commit], dict[str, list[str]]):
    """
    Parse all commits from a Git repository and return structured commit and branch data.

    This function combines `_get_commit_data` and `_get_branch_commits` to extract all
    commits along with their metadata and associates them with the branches they belong to.

    Args:
        repo_path (str): Path to the Git repository.

    Returns:
        dict[str, Commit], dict[str, list[str]]:
            - A dictionary mapping commit hashes to `Commit` objects.
            - A dictionary mapping branch names to lists of commit hashes.

    """
    commits_data = _get_commit_data(repo_path)
    branch_commits = _get_branch_commits(repo_path)

    if not commits_data:
        return {}, {}  # Empty Repo

    return commits_data, branch_commits


def _get_commit_data(repo_path: str) -> dict[str, Commit]:
    """
    Extract all commits from the Git repository and return structured commit data.

    This function uses `git log --all` with a custom pretty format to retrieve a detailed
    log of all commits, including metadata (author, date, message, parents) and changed files
    via `--numstat`. Each commit is parsed and stored in a Commit object.

    It handles commits across all branches, skipping malformed entries. For each commit,
    it also computes the number of added and deleted lines, detects binary files, and
    builds a list of changed files as `ChangedFile` instances.

    If a commit's timestamp cannot be parsed, it defaults to the Unix epoch (1970-01-01 UTC).

    Args:
        repo_path (str): The path to the Git repository.

    Returns:
        dict[str, Commit]: A dictionary mapping commit hashes to their corresponding
                           `Commit` objects, including all parsed metadata and file changes.

    """
    commits_data: dict[str, Commit] = {}

    # Thanks to https://coderwall.com/p/euwpig/a-better-git-log

    # For own Testing use:
    # git log --all --pretty=format:'%H<FIELD_SEP>%an<FIELD_SEP>%ae<FIELD_SEP>%ct<FIELD_SEP>%B<FIELD_SEP>%P<GIT_COMMIT_SEPARATOR>'

    # %H: Hash, %an: Author name, %ae: Author email, %ct: Committer date (Unix timestamp), %B: Full commit message, %P: Parent hashes
    # More -> https://git-scm.com/docs/pretty-formats/2.24.0

    commit_separator = "<GIT_COMMIT_SEPARATOR>"
    field_separator = "<FIELD_SEP>"

    log_format = f"%H{field_separator}%an{field_separator}%ae{field_separator}%ct{field_separator}%B{field_separator}%P"

    raw_log_output = run_git_command(
        ["log", "--all", f"--pretty=format:{log_format}{commit_separator}"],
        repo_path,
    )

    if not raw_log_output:
        return {}  # Empty Repository

    raw_commits = raw_log_output.split(commit_separator)

    for raw_commit_entry in raw_commits:
        if not raw_commit_entry.strip():  # Continue if empty string
            continue

        # Expects 6 parts based on log_format ->
        # 1. Hash,
        # 2. Name,
        # 3. Mail,
        # 4. Date,
        # 5. Commit MSG,
        # 6. Parent

        parts = raw_commit_entry.strip().split(field_separator)
        if len(parts) != 6:
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
        # This repo: git log -1 19c216d2 --numstat --pretty=format:

        # Example Output:
        # 138     123     main.py
        # 18      75      pyproject.toml
        # 4       0       requirements.txt

        numstat_output = run_git_command(
            ["log", "-1", commit_hash, "--numstat", "--pretty=format:"],
            repo_path,
        )

        lines_added = 0
        lines_deleted = 0
        changed_files = []

        numstat_lines = numstat_output.splitlines()
        for line in numstat_lines:
            line = line.strip()
            if not line:
                continue

            stat_parts = line.split("\t")  # Split at Tabs
            if len(stat_parts) == 3:
                added_str, deleted_str, file_path = stat_parts
                # Git doesn't track added or deleted lines in binary files, since it's not possible
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
                    ),
                )

        try:
            committer_timestamp = int(committer_timestamp_str)
            commit_date = datetime.fromtimestamp(committer_timestamp, tz=timezone.utc)
        except ValueError:
            # I am aware that this isn't the best solution Unix start time seems
            # to be the best placeholder value. Can't use None since I would force to always
            # check if None
            # Fallback: set to Unix epoch start time (1970-01-01 00:00:00 UTC)
            commit_date = datetime(1970, 1, 1, tzinfo=timezone.utc)

        # TODO: remove it since its not needed anymore - Never used parents other than I thought
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
        )  # Hash: Commit-Object

    return commits_data


def _get_branch_commits(repo_path: str) -> dict[str, list[str]]:
    """
    Collect all branches in the given Git repository and map them to their commit history.

    This function runs `git branch --all` to list all local and remote branches (excluding HEAD aliases),
    then retrieves the list of commit hashes for each branch using `git rev-list`.

    Args:
        repo_path (str): Path to the Git repository.

    Returns:
        dict[str, list[str]]: A mapping from branch names to lists of commit hashes,
                              ordered from latest to oldest.

    """
    branch_commits: dict[
        str,
        list[str],
    ] = {}  # Maps branch names to lists of commit hashes

    for branch_name in run_git_command(
        ["branch", "--all", "--format=%(refname:short)"],
        repo_path,
    ).splitlines():
        branch_name = branch_name.strip()
        if not branch_name:
            continue

        branch_commits[branch_name] = run_git_command(
            ["rev-list", branch_name],
            repo_path,
        ).splitlines()  # Branch-Name: list(commits)

    return branch_commits
