"""
Branch configuration and classification utilities.

This module provides functions to:
- Load a JSON-based configuration file for classifying Git branches.

Functions:
    load_branch_config(path): Load branch configuration from a JSON file.

"""

from __future__ import annotations

from pathlib import Path
import json


def load_branch_config(path: str | Path) -> dict:
    """Load the branch configuration from a JSON file.

    Args:
        path (str): The path to the JSON file containing branch configurations.

    Returns:
        dict: A dictionary containing the branch configurations.

    """
    with open(path) as f:
        return json.load(f)
