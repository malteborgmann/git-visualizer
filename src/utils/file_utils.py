from src.core.git_command_runner import run_git_command


def is_valid_git_repo(path: str) -> bool:
    """Checks if the given path is a valid Git repository."""

    try:
        check_for_work_tree = run_git_command(["rev-parse", "--is-inside-work-tree"], path)

        if check_for_work_tree == "true":
            return True

        check_for_bare_repo = run_git_command(["rev-parse", "--is-bare-repository"], path)

        return check_for_bare_repo == "true"
    except RuntimeError:
        return False
