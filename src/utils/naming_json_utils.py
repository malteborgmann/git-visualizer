import json


def load_name_config(path):
    """
    Load the name configuration from a JSON file.
    Args:
        path (str): The path to the JSON file containing name configurations.
    Returns:
        dict: A dictionary containing the name configurations.
    """

    with open(path, "r") as f:
        data = json.load(f)
    return data

def get_name_by_mail(mail: str, config: dict) -> str:
    """
    Get the name associated with a given email address using the provided configuration.
    Args:
        mail (str): The email address to look up.
        config (dict): A dictionary containing the name configuration.
    Returns:
        str: The name associated with the email address, or None if not found.
    """
    print("config", config)
    for name, emails in config.items():
        if mail in emails:
            return name
    return None

