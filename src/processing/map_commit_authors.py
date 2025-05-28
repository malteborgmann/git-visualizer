from pathlib import Path

from src.core.models import Repository
from src.utils.naming_json_utils import load_name_config


def _get_name_by_mail(mail: str, config: dict) -> str | None:
    """Get the name associated with a given email address using the provided configuration.

    Args:
        mail (str): The email address to look up.
        config (dict): A dictionary containing the name configuration.

    Returns:
        str: The name associated with the email address, or None if not found.

    """
    for name, emails in config.items():
        if mail in emails:
            return name
    return None

def map_commit_authors(repo: Repository, name_path: str | Path) -> None:
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
            name = _get_name_by_mail(commit.author_email, name_config)
            if name:
                commit.author_name = name
