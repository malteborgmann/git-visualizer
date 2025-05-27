"""
Branch configuration and classification utilities.

This module provides functions to:
- Load a JSON-based configuration file for classifying Git branches.
- Classify a Git branch name into categories based on regex patterns.

Functions:
    load_branch_config(path): Load branch configuration from a JSON file.
    classify_branch(branch_name, config): Classify a branch name based on regex rules.

"""
from __future__ import annotations

from pathlib import Path
import json
import re


def load_branch_config(path: str | Path) -> dict:
    """Load the branch configuration from a JSON file.

    Args:
        path (str): The path to the JSON file containing branch configurations.

    Returns:
        dict: A dictionary containing the branch configurations.

    """
    with open(path) as f:
        return json.load(f)


def classify_branch(branch_name: str, config: dict) -> str | None:
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
