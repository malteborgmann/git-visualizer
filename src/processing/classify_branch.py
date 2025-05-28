import re

from src.core.models import Repository
from src.utils.branch_json_utils import load_branch_config


def _classify_branch(branch_name: str, config: dict) -> str | None:
    """Classify a branch based on its name using the provided configuration.

    Args:
        branch_name (str): The name of the branch to classify.
        config (dict): A dictionary containing the branch classification configuration.

    """
    for category, info in config.items():
        pattern = info["pattern"]
        # re.search searches for the pattern that is given in the config
        if re.search(pattern, branch_name):
            return category
    return None

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
        branch.category = _classify_branch(branch.name, branch_config)
