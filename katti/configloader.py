import os
from datetime import datetime
import json
import configparser
import sys
from dataclasses import dataclass
from katti import constants

user_config_changed = False
problems_config_changed = False
unsolved_problems_config_changed = False

@dataclass
class KattisConfig:
    '''A dataclass representing the kattis config file. URL contains "https://" '''
    username: str
    url: str
    token: str
    password: str

def load_user_config(config_path: str) -> dict:
    """Loads the user config file and returns it as a dict

    Parameters:
    ----------
    config_path: str
        A string representing the absolute path to the user config file

    Returns:
    -------
    dict 
        A dictionary containing the user config
    """
    global user_config_changed
    user_config = None
    if not os.path.exists(config_path):
        user_config = {
                "ids_last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "ratings_update_period": constants.DEFAULT_RATING_UPDATE_PERIOD
        }
        user_config_changed = True
    else:
        with open(config_path, "r") as f:
            user_config = json.load(f)
        if not user_config:
            user_config = {
                "ids_last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "ratings_update_period": constants.DEFAULT_RATING_UPDATE_PERIOD
            }
            user_config_changed = True
    return user_config


def load_problems_config(config_path: str) -> dict:
    """Loads the problems config file and returns it as a dict

    Parameters:
    ----------
    config_path: str
        A string representing the absolute path to the problems config file

    Returns:
    -------
    dict 
        A dictionary containing the problems config
    """
    problems_list = None
    if not os.path.exists(config_path):
        problems_list = {}
        problems_config_changed = True
    else:
        with open(config_path, "r") as f:
            problems_list = json.load(f)
        if not problems_list:
            problems_list = {}
            problems_config_changed = True
    return problems_list

def load_unsolved_problems_config(config_path: str) -> dict:
    """Loads the unsolved problems file and returns it as a dict

    Parameters:
    ----------
    config_path: str
        A string representing the absolute path to the unsolved problems file

    Returns:
    -------
    dict 
        A dictionary containing the unsolved problems
    """
    unsolved_problems = None
    if not os.path.exists(config_path):
        unsolved_problems = {}
        unsolved_problems_config_changed = True
    else:
        with open(config_path, "r") as f:
            unsolved_problems = json.load(f)
        if not unsolved_problems:
            unsolved_problems = {}
            unsolved_problems_config_changed  = True
    return unsolved_problems

def load_selected_problems_config(config_path: str) -> dict:
    """Loads the selected problems file and returns it as a dict

    Parameters:
    ----------
    config_path: str
        A string representing the absolute path to the selected problems file

    Returns:
    -------
    dict 
        A dictionary containing the selected problems
    """
    selected_problems = None
    if not os.path.exists(config_path):
        selected_problems = {}
        selected_problems_config_changed = True
    else:
        with open(config_path, "r") as f:
            selected_problems = json.load(f)
        if not selected_problems:
            selected_problems = {}
            selected_problems_config_changed = True
    return selected_problems


def problem_config_changed():
    """Ensures that the problems config file is saved when the program exits"""
    global problems_config_changed
    problems_config_changed = True

def unsolved_problems_config_changed():
    """Ensures that the unsolved problems file is saved when the program exits"""
    global unsolved_problems_config_changed
    unsolved_problems_config_changed = True


def update_user_config():
    """Ensures that the user config file is saved when the program exits"""
    global user_config_changed
    user_config_changed = True


def save_user_config(config_path: str, user_config: dict):
    """Saves the user config file

    Parameters:
    ----------
    config_path: str
        A string representing the absolute path to the user config file
    user_config: dict
        A dictionary containing the user config
    """
    global user_config_changed
    if user_config_changed:
        with open(config_path, "w") as f:
            json.dump(user_config, f, indent=4)
        user_config_changed = False


def save_problems_config(config_path: str, problems_config: dict):
    """Saves the problems config file

    Parameters:
    ----------
    config_path: str
        A string representing the absolute path to the problems config file
    problems_config: dict
        A dictionary containing the problems config
    """
    global problems_config_changed
    if problems_config_changed:
        with open(config_path, "w") as f:
            json.dump(problems_config, f)
        problems_config_changed = False

def save_unsolved_problems_config(config_path: str, unsolved_problems: dict):
    """Saves the unsolved problems file

    Parameters:
    ----------
    config_path: str
        A string representing the absolute path to the unsolved problems file
    unsolved_problems: dict
        A dictionary containing the unsolved problems
    """
    global unsolved_problems_config_changed
    if unsolved_problems_config_changed:
        with open(config_path, "w") as f:
            json.dump(unsolved_problems, f)
        unsolved_problems_config_changed = False

def get_kattis_config(config_path: str) -> KattisConfig:
    """Helper function to load a users .kattisrc file and parse it

    Parameters:
    ----------
    config_path: str
        A string representing the absolute path to the .kattisrc file

    Returns:
    -------
    tuple
        A tuple containing (username, url, token) as strings
    """
    config = configparser.ConfigParser()
    if not config.read([config_path]):
        print("Unable to locate .kattisrc file")
        print(
            "Please navigate to https://open.kattis.com/help/submit to download a new .kattisrc")
        print("Aborting...")
        sys.exit(1)

    username = config.get("user", "username")
    token = None
    url = None
    password = None
    try:
        token = config.get("user", "token")
        url = config.get("kattis", "hostname")
        password = config.get("user", "password")
    except configparser.NoOptionError:
        pass
    if token is None or url is None:
        print("Corrupted .kattisrc file")
        print("Please navigate to https://open.kattis.com/help/submit and download a new .kattisrc")
        print("Aborting...")
        sys.exit(1)
    if password is None:
        pass
    url = "https://" + url
    return KattisConfig(username, url, token, password)
