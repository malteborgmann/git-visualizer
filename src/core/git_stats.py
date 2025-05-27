from typing import List, Tuple
import os

from src.core.git_command_runner import run_git_command


def _get_ignored_paths(repo_path: str) -> List[str]:
    """Liefert alle Dateien/Verzeichnisse zurück, die laut .gitignore ignoriert werden.
    """
    output = run_git_command(
        ["ls-files", "--others", "--ignored", "--exclude-standard", "--directory"],
        repo_path,
    )
    # Jede Zeile ist relativ zum repo_path
    return [line for line in output.splitlines() if line.strip()]


def _get_hooks(repo_path: str) -> List[str]:
    """Listet alle Hook-Skripte im .git/hooks-Verzeichnis (ohne .sample-Dateien).
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
    """Zählt die Gesamtzahl der Zeilen in allen getrackten Dateien des Repos.
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
            # kann z.B. bei Binärdateien oder fehlenden Rechten passieren
            continue
    return total


def get_repo_stats(repo_path: str) -> Tuple[int, int, int, List[str]]:
    """Liefert ein Tupel (total_files, ignored_count, loc, hooks_list).
    """
    # Gesamtzahl der getrackten Dateien
    files = run_git_command(["ls-files"], repo_path).splitlines()
    total_files = len(files)

    ignored = _get_ignored_paths(repo_path)
    ignored_count = len(ignored)

    loc = _count_lines_of_code(repo_path)
    hooks = _get_hooks(repo_path)

    return total_files, ignored_count, loc, hooks
