import json
import os
import re


def check_path_exists(path):
    """
    Check if the given path exists.

    Args:
        path (str): The path to check.

    Returns:
        bool: True if the path exists, False otherwise.
    """
    return os.path.exists(path)


def load_branch_config(path):
    """
    Load the branch configuration from a JSON file.

    Args:
        path (str): The path to the JSON file containing branch configurations.

    Returns:
        dict: A dictionary containing the branch configurations.
    """
    with open(path, "r") as f:
        data = json.load(f)
    return data


def classify_branch(branch_name: str, config: dict) -> str | None:
    """
    Classify a branch based on its name using the provided configuration.
    Args:
        branch_name (str): The name of the branch to classify.
        config (dict): A dictionary containing the branch classification configuration.
    """
    for category, info in config.items():
        pattern = info["pattern"]
        if re.match(pattern, branch_name):
            return category
    return None


if __name__ == "__main__":
    path = "./config/example_branches.json"
    branch_config = load_branch_config(path)
    print(branch_config["feature"]["pattern"])

    for name in ["feature/123-add-login", "bugfix/42-fix-error", "docs/readme"]:
        cat = classify_branch(name, branch_config)
        if cat:
            print(f"Branch `{name}` gehört zu `{cat}`.")
        else:
            print(f"Branch `{name}` gehört zu keiner definierten Kategorie.")
