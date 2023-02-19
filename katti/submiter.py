import configparser
import sys
import os

_HEADERS = {"User-Agent": "kattis-cli-submit"}


def get_config() -> configparser.ConfigParser:
    """Helper function to load a users .kattisrc file from home directory

    Parameters:
    ----------
    None

    Returns
    -------
    A ConfigParser object containing the users .kattisrc file
    """
    config = configparser.ConfigParser()
    if not config.read([os.path.join(os.getenv("HOME"), ".kattisrc")]):
        print("Unable to locate .kattisrc file")
        print(
            "Please navigate to https://open.kattis.com/help/submit to download a new one")
        print("Aborting...")
        sys.exit(0)
    return config


def parse_config(config: configparser.ConfigParser) -> tuple:
    """Helper function for login. Parses a config file for username and submit token.
    On failure to parse config file, exits control flow

    Parameters:
    ----------
    config: ConfigParser 

    Returns:
    -------
    tuple 
        A tuple containing the username and submit token
    """
    username = config.get("user", "username")
    token = None
    try:
        token = config.get("user", "token")
    except configparser.NoOptionError:
        pass
    if token is None:
        print("Corrupted .kattisrc file")
        print("Please navigate to https://open.kattis.com/help/submit and download a new .kattisrc")
        print("Aborting...")
        sys.exit(1)
    return (username, token)
