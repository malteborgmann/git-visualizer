import os
from typing import List, Tuple
from src.core.git_command_runner import run_git_command


def _get_ignored_paths(repo_path: str, matched_ignores: List = []) -> List[str]:
    """
    Such nach allen .gitignore dateien im Projekt und fügt diese hinzu
    Args:
        repo_path:
        matched_ignores: List -> Gib mir eine Liste an von Pfaden, die bereits ignoriert sind

    Returns:

    """
    gitignore_files = []
    patterns = set()

    # ------------------------------------------------------------
    is_ignored = lambda sp: any(
        sp == pat.rstrip('/') or sp.startswith(pat.rstrip('/'))
        for pat in matched_ignores
    )
    # ------------------------------------------------------------

    for path, _, files in os.walk(repo_path):
        striped_path = path.replace(repo_path, "") # Liefert den relativen Pfad
        if is_ignored(striped_path):
            continue
            # Das hier mache ich tatsächlich nur, damit ich nicht
            # gitignores aus bereits ignorierten Pfaden mit reinnehme

        if ".gitignore" in files:
            gitignore_files.append(os.path.join(path, ".gitignore"))

    for file in gitignore_files:
        with open(file, "r") as f:
            lines = map(lambda s: str(s).replace("\n", ""), f.readlines())
            lines = filter(lambda s: not str(s).strip().startswith("#"), lines)
            patterns = patterns.union(lines)
    return list(patterns)


def _get_ignored_files(repo_path: str) -> List[str]:
    """
    Liefert alle Dateien/Verzeichnisse zurück, die laut .gitignore ignoriert werden.
    """
    print(repo_path)
    output = run_git_command(
        ["ls-files", "--others", "--ignored", "--exclude-standard", "--directory"],
        repo_path,
    )
    return [line for line in output.splitlines() if line.strip()]


def _get_hooks(repo_path: str) -> List[str]:
    """
    Listet alle Hook-Skripte im .git/hooks-Verzeichnis (ohne .sample-Dateien).
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
    Zählt die Gesamtzahl der Zeilen in allen getrackten Dateien des Repos.
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


def get_repo_stats(repo_path: str) -> tuple[list[str], list[str], list[str], list[str], int]:
    """
    Liefert ein Tupel (total_files, ignored_count, loc, hooks_list).
    """
    # Gesamtzahl der getrackten Dateien
    total_files = run_git_command(["ls-files"], repo_path).splitlines()

    ignored_matched = _get_ignored_files(repo_path)

    ignored_pattern = _get_ignored_paths(repo_path, matched_ignores=ignored_matched)

    loc = _count_lines_of_code(repo_path)
    hooks = _get_hooks(repo_path)

    return total_files, ignored_matched, ignored_pattern, hooks, loc

if __name__ == '__main__':
    print(_get_ignored_paths("/Users/malteborgmann/Projects/git-visualizer/"))