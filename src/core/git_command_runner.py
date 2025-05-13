import subprocess
from typing import List, Dict, Tuple


def run_git_command(command: List[str], repo_path: str) -> str:
    """Executes a Git command in the specified repository path and returns its output."""
    try:
        result = subprocess.run(
            ["git", "-C", repo_path] + command,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",  # Important for correct character encoding
        )
        return result.stdout.strip()
    except FileNotFoundError:
        raise RuntimeError(
            "Git command not found. Please ensure Git is installed and in your PATH."
        )
    except subprocess.CalledProcessError as e:
        error_message = f"Git command failed with error: {e.stderr.strip()}"
        if (
            "not a git repository" in e.stderr.lower()
            or "fatal: Invalid gitfile format" in e.stderr.lower()
            or "detected dubious ownership in repository at" in e.stderr.lower()
        ):
            try:
                git_dir_arg = f"--git-dir={repo_path}/.git"
                work_tree_arg = f"--work-tree={repo_path}"
                base_command = ["git", git_dir_arg, work_tree_arg]

                # Test if it is a bare repo
                is_bare_check = subprocess.run(
                    base_command + ["rev-parse", "--is-bare-repository"],
                    capture_output=True,
                    text=True,
                    check=False,
                    encoding="utf-8",
                )
                if is_bare_check.stdout.strip() == "true":
                    base_command = [
                        "git",
                        f"--git-dir={repo_path}",
                    ]  # For bare repos, work-tree is not necessary

                result = subprocess.run(
                    base_command + command,
                    capture_output=True,
                    text=True,
                    check=True,
                    encoding="utf-8",
                )
                return result.stdout.strip()
            except subprocess.CalledProcessError as e2:
                error_message = f"Git command failed: {e.stderr.strip()}. Secondary attempt failed: {e2.stderr.strip()}"
                raise ValueError(
                    f"The path '{repo_path}' is not a valid Git repository or cannot be accessed. Error: {error_message}"
                )
        raise RuntimeError(error_message)
