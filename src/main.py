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
        print(f"Number Branches: {len(repository_data.branches)}")

        # Zeige Branch-Details
        if repository_data.branches:
            print("\nBranch Details (max. 3 pro Typ):")
            max_each_type = 3

            print("  Local Branches:")
            count = 0
            for branch_name, branch in repository_data.branches.items():
                if not branch.is_remote and count < max_each_type:
                    default_marker = " (default)" if branch.is_default else ""
                    print(f"    - {branch_name}{default_marker}")
                    print(f"      HEAD: {branch.head_commit_hash[:7]}")
                    print(f"      Commits: {len(branch.commits)}")
                    
                    # Zeige die letzten 2 Commits dieses Branches
                    if branch.commits:
                        print("      Recent Commits:")
                        for i, (commit_hash, commit) in enumerate(branch.commits.items()):
                            if i >= 2:  # Nur die letzten 2 Commits zeigen
                                break
                            print(f"        - {commit_hash[:7]}: {commit.message.splitlines()[0]} : Added: {commit.lines_added} - Deleted: {commit.lines_deleted}")
                    count += 1
            if count == 0:
                print("      No local branches found or displayed.")
            
            print("\n  Remote Branches:")
            count = 0
            for branch_name, branch in repository_data.branches.items():
                if branch.is_remote and count < max_each_type:
                    default_marker = " (default)" if branch.is_default else ""
                    print(f"    - {branch_name}{default_marker}")
                    print(f"      HEAD: {branch.head_commit_hash[:7]}")
                    print(f"      Commits: {len(branch.commits)}")
                    
                    # Zeige die letzten 2 Commits dieses Branches
                    if branch.commits:
                        print("      Recent Commits:")
                        for i, (commit_hash, commit) in enumerate(branch.commits.items()):
                            if i >= 2:  # Nur die letzten 2 Commits zeigen
                                break
                            print(f"        - {commit_hash[:7]}: {commit.message.splitlines()[0]}")
                    count += 1
            if count == 0:
                print("      No remote branches found or displayed.")

    except ValueError as e:
        print(f"ValueError during analyzation: {e}")
    except RuntimeError as e:
        print(f"RuntimeError: {e}")
    except Exception as e:
        print(f"An unexpected Exception occured: {e}")

if __name__ == "__main__":
    main() 