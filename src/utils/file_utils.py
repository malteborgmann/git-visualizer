import os
import subprocess


def is_valid_git_repo(path: str) -> bool:
    """Checks if the given path is a valid Git repository."""
    git_dir = os.path.join(path, ".git")
    if not os.path.isdir(git_dir):
        if os.path.basename(path) == ".git" and os.path.isdir(path):
            pass  # TODO: Implement later
        elif not os.path.isdir(git_dir):
            return False

    try:
        check_is_work_tree = subprocess.run(
            ["git", "-C", path, "rev-parse", "--is-inside-work-tree"],
            check=False,  # Do not throw an error here directly
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        is_work_tree = (
            check_is_work_tree.returncode == 0
            and check_is_work_tree.stdout.strip() == "true"
        )

        if is_work_tree:
            return True

        check_is_bare = subprocess.run(
            ["git", "-C", path, "rev-parse", "--is-bare-repository"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        is_bare = (
            check_is_bare.returncode == 0 and check_is_bare.stdout.strip() == "true"
        )

        return is_bare

    except FileNotFoundError:
        # Git is not installed or not in PATH
        return False
    except subprocess.CalledProcessError:
        # The command failed, which can happen in a non-repo directory
        return False


def export_to_markdown(data, output_file: str):
    """Placeholder for Markdown export."""
    # TODO: Implement Markdown export
    print(f"Data would be exported to {output_file} as Markdown (not yet implemented).")


def export_to_csv(data, output_file: str):
    """Placeholder for CSV export."""
    # TODO: Implement CSV export
    print(f"Data would be exported to {output_file} as CSV (not yet implemented).")
