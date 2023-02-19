import configparser
import sys
import os
import webbrowser
import requests
from bs4 import BeautifulSoup
from katti import configloader

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


def show_description(problem_id: str, problems_config: dict, verbose=False):
    """Opens a problem description in the default browser.
    If the problem is not in the problems config file, but is on the web, it will be added to the problems config file.

    Parameters
    ----------
    problem_id: str
        A string representing the problem id
    problems_config: dict
        A dictionary containing problem ids and their corresponding problem names
    verbose: bool
        A boolean flag to enable verbose mode
    Returns:
    -------
    None
    """
    if problem_id not in problems_config:
        print(
            f"Could not find {problem_id} in problem_ids, checking web") if verbose else None
        problem_rating = get_problem_rating(problem_id, verbose)
        if not problem_rating:
            print(f"Invalid problem ID: {problem_id}")
            print("Aborting...")
            sys.exit(1)
        else:
            print("Problem found on web, adding to problem_ids") if verbose else None
            problems_config[problem_id] = problem_rating
            configloader.problem_config_changed()

    if input('Open in browser? [Y/n]: ').lower() not in {'n', 'no'}:
        webbrowser.open("https://open.kattis.com/problems/" + problem_id)


def get_problem_rating(problem_id: str, verbose=False) -> str:
    """
    Helper function to get the current rating of problem from Kattis

    Parameters:
    ----------
    problem_id: str
        A string representing the problem id
    verbose: bool
        A boolean flag to enable verbose mode

    Returns:
    -------
    str
        A string representing the problem rating
    """
    print("Making http request: https://open.kattis.com/problems/" +
          problem_id) if verbose else None
    r = requests.get("https://open.kattis.com/problems/" + problem_id)
    # bad request
    if r.status_code != 200:
        print(f"URL {r.url} returned non 200 status.")
        print("Aborting...")
        sys.exit(1)
    print("Parsing html...") if verbose else None
    soup = BeautifulSoup(r.text, 'html.parser')
    results = soup.find('span', class_='difficulty_number')
    rating = results.text
    print(f"Problem rating for {problem_id}: {rating}") if verbose else None
    return rating
