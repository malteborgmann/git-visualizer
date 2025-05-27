"""Git Repository Visualizer Entry Script.

Parses arguments, validates the repo and config files, collects metadata,
and starts the TUI visualizer.
"""
from __future__ import annotations

from argparse import Namespace
from datetime import datetime, timedelta
from pathlib import Path
import argparse

from src.core.git_parser import load_repository_data
from src.core.models import Repository
from src.tui.app_tui import GitVisualizerApp
from src.utils.branch_json_utils import classify_branch, load_branch_config
from src.utils.file_utils import is_valid_git_repo
from src.utils.naming_json_utils import get_name_by_mail, load_name_config
from src.utils.user_commits import get_commits_per_user


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


def validate_paths(repo_path: Path, branch_config_path: Path | None, branch_names_path: Path | None) \
        -> None:
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


def classify_branches(repo: Repository, config_path: str) -> None:
    """
    Classifies branches of a repository based on a given configuration.

    This function iterates over each branch in the repository and assigns
    a category to it. The category for each branch is determined using
    the provided configuration file, which defines the classification rules.

    Args:
        repo: The repository object containing branch information.
        config_path: Path to the configuration file used for branch
            classification.

    Returns:
        None

    """
    branch_config = load_branch_config(config_path)
    for branch in repo.branches.values():
        branch.category = classify_branch(branch.name, branch_config)


def map_commit_authors(repo, name_path) -> None:
    """
    Map the author of a commit to their names based on their email.

    Maps commit authors in a repository to their respective names based on a provided
    configuration file. This function iterates through all the branches and commits
    in a repository, updates the author name of each commit using the configured
    mapping of email addresses to names, and sets the updated name if a match is found.

    Args:
        repo: Repository object containing branches and commits to map authors for.
        name_path: Path to the configuration file that contains email-to-name mappings.

    Returns:
        None

    """
    name_config = load_name_config(name_path)
    for branch in repo.branches.values():
        for commit in branch.commits.values():
            name = get_name_by_mail(commit.author_email, name_config)
            if name:
                commit.author_name = name


def compute_user_commit_stats(repo):
    for branch in repo.branches.values():
        user_commits = get_commits_per_user(branch)
        branch.user_commits = dict(sorted(user_commits.items(), key=lambda x: x[1], reverse=True))


def compute_day_commit_stats(repo):
    fmt = "%d/%m/%Y"
    for branch in repo.branches.values():
        day_counts = {}
        for commit in branch.commits.values():
            day = commit.date.date().strftime(fmt)
            day_counts[day] = day_counts.get(day, 0) + 1

        # Fill in missing days
        first = datetime.strptime(min(day_counts), fmt)
        last = datetime.strptime(max(day_counts), fmt)
        current = first
        while current <= last:
            day = current.strftime(fmt)
            day_counts.setdefault(day, 0)
            current += timedelta(days=1)

        branch.day_commits = dict(sorted(day_counts.items(), key=lambda x: datetime.strptime(x[0], fmt)))


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
