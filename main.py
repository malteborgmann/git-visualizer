"""Git Repository Visualizer Entry Script.

Parses arguments, validates the repo and config files, collects metadata,
and starts the TUI visualizer.
"""

from __future__ import annotations

from argparse import Namespace

from pathlib import Path
import argparse

from src.core.git_parser import load_repository_data
from src.tui.app_tui import GitVisualizerApp
from src.utils.file_utils import is_valid_git_repo
from src.processing.map_commit_authors import map_commit_authors
from src.processing.classify_branch import classify_branches
from src.processing.user_commits import compute_user_commit_stats
from src.processing.day_commits import compute_day_commit_stats



def parse_args() -> Namespace:
    """
    Parse command-line arguments for configuring the Git Repository Visualizer and Analyzer.

    This function creates an argument parser and defines several command-line arguments that
    configure the behavior of the visualizer and analyzer. These arguments allow users to
    specify the path to a Git repository, a branch configuration file, and a name mapping file.

    Returns:
        argparse.Namespace: An object containing the parsed arguments and their values.

    """
    parser = argparse.ArgumentParser(description="Git Repository Visualizer and Analyzer")
    parser.add_argument("repo_path", nargs="?", default=".", help="Path to the Git repository")
    parser.add_argument("-b", "--branches", default=None, help="Path to the branch config file")
    parser.add_argument("-n", "--names", default=None, help="Path to the name mapping file")
    return parser.parse_args()


def validate_paths(
    repo_path: Path, branch_config_path: Path | None, branch_names_path: Path | None
) -> None:
    """
    Validate required file system paths for the Git repository and optional configuration files.

    Raises:
        FileNotFoundError: If any of the required paths do not exist or are invalid.

    """
    if not is_valid_git_repo(repo_path):
        msg = f"'{repo_path}' is not a valid Git repository."
        raise FileNotFoundError(msg)

    if branch_config_path and not Path.exists(branch_config_path):
        msg = f"Branch config file not found: '{branch_config_path}'"
        raise FileNotFoundError(msg)

    if branch_names_path and not Path.exists(branch_names_path):
        msg = f"Name mapping file not found: '{branch_names_path}'"
        raise FileNotFoundError(msg)




def main():
    args = parse_args()
    repo_path = Path.absolute(Path(args.repo_path).resolve())
    branch_config_path = Path.absolute(Path(args.branches).resolve()) if args.branches else None
    branch_names_path = Path.absolute(Path(args.names).resolve()) if args.names else None

    print(f"Analyzing: {repo_path}")

    validate_paths(repo_path, branch_config_path, branch_names_path)

    try:
        repo = load_repository_data(repo_path)

        if branch_config_path:
            classify_branches(repo, branch_config_path)

        if branch_names_path:
            map_commit_authors(repo, branch_names_path)

        compute_user_commit_stats(repo)
        compute_day_commit_stats(repo)

        app = GitVisualizerApp(repository=repo)
        app.run()

    except (RuntimeError, Exception) as e:
        print(f"Error during analysis: {e}")


if __name__ == "__main__":
    main()
