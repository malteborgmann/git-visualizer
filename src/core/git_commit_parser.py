from datetime import datetime, timezone
from typing import List, Dict, Tuple

from src.core.models import Commit, ChangedFile
from src.core.git_command_runner import run_git_command


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

    raw_log_output = run_git_command(
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
        numstat_output = run_git_command(
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

    for branch_name in run_git_command(
        ["branch", "--all", "--format=%(refname:short)"], repo_path
    ).splitlines():
        if "HEAD ->" in branch_name:
            continue
        branch_name = branch_name.strip()
        if not branch_name:
            continue

        branch_commits[branch_name] = run_git_command(
            ["rev-list", branch_name], repo_path
        ).splitlines()

    return commits_data, branch_commits
