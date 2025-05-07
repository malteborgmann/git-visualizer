# This file is used for testing and development purposes for now.
# Later on, it will be used to run the main program -> Need to clean up the code and remove the prints

import argparse
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from core.git_parser import load_repository_data
from utils.file_utils import is_valid_git_repo

def main():
    parser = argparse.ArgumentParser(description="Git Repository Visualizer and Analyzer")
    parser.add_argument(
        "repo_path", 
        nargs="?", 
        default=".", 
        help="Path to the Git repository (default: current directory)"
    )
    args = parser.parse_args()

    repo_path = os.path.abspath(args.repo_path)

    print(f"Analyzing: {repo_path}")

    if not is_valid_git_repo(repo_path):
        print(f"Error: The specified path '{repo_path}' is not a valid Git repository or Git is not correctly installed/configured.")
        print("Ensure that Git is installed and that you have the necessary permissions for the repository.")
        return

    try:
        repository_data = load_repository_data(repo_path)
        
        print(f"\nQueried Repository")
        print(f"Path: {repository_data.path}")
        print(f"Number Commits: {len(repository_data.commits)}")
        print(f"Number Branches (local and remote): {len(repository_data.branches)}")

        # Done: Details für Commits anzeigen, die nicht in einem Branch sind
        if repository_data.commits:
            print("\nCommit Details (max. 3):")
            for i, (commit_hash, commit) in enumerate(repository_data.commits.items()):
                if i >= 3:
                    break
                print(f"  Commit: {commit_hash[:7]}")
                print(f"    Autor: {commit.author_name} <{commit.author_email}>")
                print(f"    Date: {commit.date.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                message_first_line = commit.message.splitlines()[0] if commit.message else "(Keine Nachricht)"
                print(f"    Message: {message_first_line}")
                print(f"    Lines Added: {commit.lines_added}, Lines Deleted: {commit.lines_deleted}")
                parents_str = ", ".join([p[:7] for p in commit.parents]) if commit.parents else "(Initialer Commit)"
                print(f"    Parents: {parents_str}")
        
        # Done: Details für Branches anzeigen, die nicht in einem Branch sind
        if repository_data.branches:
            print("\nBranch Details (max. 3):")
            local_branches_shown = 0
            remote_branches_shown = 0
            max_each_type = 3

            print("  Local Branches:")
            count = 0
            for branch_name, branch in repository_data.branches.items():
                if not branch.is_remote and count < max_each_type:
                    print(f"    - {branch_name} (HEAD: {branch.head_commit_hash[:7]})")
                    count +=1
            if count == 0: print("      No local branches found or displayed.")
            
            print("  Remote Branches:")
            count = 0
            for branch_name, branch in repository_data.branches.items():
                if branch.is_remote and count < max_each_type:
                    print(f"    - {branch_name} (HEAD: {branch.head_commit_hash[:7]})")
                    count +=1
            if count == 0: print("      No remote branches found or displayed.")

    except ValueError as e:
        print(f"ValueError during analyzation: {e}")
    except RuntimeError as e:
        print(f"RuntimeError: {e}")
    except Exception as e:
        print(f"An unexpected Exception occured: {e}")

if __name__ == "__main__":
    main() 