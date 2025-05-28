"""
Name mapping utilities based on email addresses.

This module provides functions to:
- Load a JSON configuration file that maps names to lists of email addresses.

Functions:
    load_name_config(path): Load name configuration from a JSON file.

"""

from __future__ import annotations

from pathlib import Path
import json


def load_name_config(path: str | Path) -> dict:
    """Load the name configuration from a JSON file.

    Args:
        path (str): The path to the JSON file containing name configurations.

    Returns:
        dict: A dictionary containing the name configurations.

    """
    with open(path) as f:
        return json.load(f)