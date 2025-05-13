# This file is used for testing and development purposes for now.
# Later on, it will be used to run the main program -> Need to clean up the code and remove the prints

import argparse
import os
import sys
import json

from src.core.git_parser import load_repository_data
from src.utils.file_utils import is_valid_git_repo
from src.tui.app_tui import GitVisualizerApp
from src.utils.branch_json_utils import classify_branch, load_branch_config
from src.utils.naming_json_utils import load_name_config, get_name_by_mail
from src.utils.user_commits import get_commits_per_user


def main():
    parser = argparse.ArgumentParser(
        description="Git Repository Visualizer and Analyzer"
    )
    parser.add_argument(
        "repo_path",
        nargs="?",
        default=".",
        help="Path to the Git repository (default: current directory)",
    )
    parser.add_argument(
        "-b",
        "--branches",
        default=None,
        help="Path to the branches file (default: None)",
    )

    parser.add_argument(
        "-n",
        "--names",
        default=None,
        help="Path to the names file (default: None)",
    )

    args = parser.parse_args()

    repo_path = os.path.abspath(args.repo_path)
    branch_config_path = os.path.abspath(args.branches) if args.branches else None
    branch_names_path = os.path.abspath(args.names) if args.names else None
    # branch_config_path = os.path.abspath("./config/example_branches.json") # TODO: Remove for later version - Just for testing

    print(f"Analyzing: {repo_path}")

    if not is_valid_git_repo(repo_path):
        print(
            f"Error: The specified path '{repo_path}' is not a valid Git repository or Git is not correctly installed/configured."
        )
        print(
            "Ensure that Git is installed and that you have the necessary permissions for the repository."
        )
        return

    if branch_config_path and not os.path.exists(branch_config_path):
        print(
            f"Error: The specified branch config path '{branch_config_path}' does not exist."
        )
        return

    if branch_names_path and not os.path.exists(branch_names_path):
        print(
            f"Error: The specified branch names path '{branch_names_path}' does not exist."
        )
        return

    try:
        # Categorize branches based on the branch_config
        repository_data = load_repository_data(repo_path)
        if branch_config_path:
            branch_config = load_branch_config(branch_config_path)
            for branch in repository_data.branches.values():
                branch.category = classify_branch(branch.name, branch_config)

        # Replace names with the ones from the names file
        if branch_names_path:
            name_config = load_name_config(branch_names_path)
            for branch in repository_data.branches.values():
                for commit in branch.commits.values():
                    name = get_name_by_mail(commit.author_email, name_config)
                    if name:
                        commit.author_name = name

        for branch in repository_data.branches.values():
            branch.user_commits = get_commits_per_user(branch)
            branch.user_commits = dict(sorted(
                branch.user_commits.items(), key=lambda x: x[1], reverse=True
            ))
            print(f"Branch: {branch.name}, User Commits: {branch.user_commits.keys()}")


        print("\nQueried Repository")
        print(f"Path: {repository_data.path}")
        print(f"Number Branches: {len(repository_data.branches)}")

        for key, branch in repository_data.branches.items():
            print(f"Branch: {key}")
            print(f"  Head Commit: {branch.head_commit_hash}")
            print(f"  Is Remote: {branch.is_remote}")
            print(f"  Is Default: {branch.is_default}")
            print(f"  Number of Commits: {len(branch.commits)}")
            for commit_hash, commit in branch.commits.items():
                print(
                    f"    Commit: {commit_hash} by {commit.author_name} on {commit.date}"
                )
            break

        app = GitVisualizerApp(repository=repository_data)
        app.run()

    except ValueError as e:
        print(f"ValueError during analyzation: {e}")
    except RuntimeError as e:
        print(f"RuntimeError: {e}")
    except Exception as e:
        print(f"An unexpected Exception occured: {e}")


if __name__ == "__main__":
    main() 