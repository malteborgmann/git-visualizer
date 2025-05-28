import os

from src.core.git_command_runner import run_git_command


def _get_ignored_paths(repo_path: str) -> list[str]:
    """
    Return a list of paths ignored by Git, based on .gitignore and standard exclusions.

    Uses `git ls-files` with flags to list files that are:
    - untracked (`--others`)
    - ignored (`--ignored`)
    - excluded via .gitignore, .git/info/exclude, or core.excludesFile (`--exclude-standard`)
    - directories (`--directory`)

    Args:
        repo_path (str): Absolute path to the Git repository.

    Returns:
        list[str]: Relative paths from repo root of all ignored files and directories.

    """
    output = run_git_command(
        ["ls-files", "--others", "--ignored", "--exclude-standard", "--directory"],
        repo_path,
    )
    return [line for line in output.splitlines() if line.strip()] # Do not add empty lines


def _get_hooks(repo_path: str) -> list[str]:
    """
    Return a list of executable Git hook scripts present in the .git/hooks directory.

    Ignores files ending in .sample, and only includes executable files (Unix `+x`).

    Args:
        repo_path (str): Absolute path to the Git repository.

    Returns:
        list[str]: Names of active Git hook scripts (e.g., `pre-commit`, `post-merge`).

    """
    hooks_dir = os.path.join(repo_path, ".git", "hooks")
    if not os.path.isdir(hooks_dir):
        return []
    hooks = []
    for name in os.listdir(hooks_dir):
        if name.endswith(".sample"):
            continue
        full = os.path.join(hooks_dir, name)
        if os.path.isfile(full) and os.access(full, os.X_OK):
            hooks.append(name)
    return hooks


def _count_lines_of_code(repo_path: str) -> int:
    """
    Count the total number of lines across all tracked text files in the repository.

    Uses `git ls-files` to identify tracked files and reads them line by line.
    Files that cannot be read (e.g., binaries or permission issues) are silently skipped.

    Args:
        repo_path (str): Absolute path to the Git repository.

    Returns:
        int: Total number of lines of code (LOC) across tracked files.

    """
    # Alle getrackten Dateien per git ls-files
    output = run_git_command(["ls-files"], repo_path)
    total = 0
    for rel_path in output.splitlines():
        path = os.path.join(repo_path, rel_path)
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                total += sum(1 for _ in f)
        except OSError:
            # Error is caused by two things: Missing permission or binary file
            print(f"Cant read file: {path}. ")
            continue
    return total


def get_repo_stats(repo_path: str) -> (int, int, int, list[str]):
    """
    Gather basic repository statistics including tracked file count, ignored paths, lines of code, and available Git hooks.

    This function serves as a summary aggregator using helper functions for:
    - Total number of tracked files
    - Number of ignored paths
    - Total lines of code in tracked files
    - List of hook scripts in `.git/hooks`

    Args:
        repo_path (str): Absolute path to the Git repository.

    Returns:
        Tuple[int, int, int, List[str]]:
            - total_files (int): Number of tracked files
            - ignored_count (int): Number of ignored paths
            - loc (int): Total lines of code
            - hooks (list[str]): List of Git hook script names

    """  # noqa: E501
    files = run_git_command(["ls-files"], repo_path).splitlines()
    total_files = len(files)

    ignored = _get_ignored_paths(repo_path)
    ignored_count = len(ignored)

    loc = _count_lines_of_code(repo_path)
    hooks = _get_hooks(repo_path)

    return total_files, ignored_count, loc, hooks
