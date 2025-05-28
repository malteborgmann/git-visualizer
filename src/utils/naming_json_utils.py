"""
Name mapping utilities based on email addresses.

This module provides functions to:
- Load a JSON configuration file that maps names to lists of email addresses.
- Retrieve a human-readable name for a given email address using the loaded mapping.

Functions:
    load_name_config(path): Load name configuration from a JSON file.
    get_name_by_mail(mail, config): Look up the name associated with a given email address.

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


def get_name_by_mail(mail: str, config: dict) -> str | None:
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
