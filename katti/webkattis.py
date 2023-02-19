import configparser
import sys
import os
import webbrowser
import requests
from bs4 import BeautifulSoup
from katti import configloader

# URLs
_LOGIN_URL = "https://open.kattis.com/login"
_SUBMIT_URL = "https://open.kattis.com/submit"
_STATUS_URL = "https://open.kattis.com/submissions/"

_HEADERS = {"User-Agent": "kattis-cli-submit"}


def show_description(problem_id: str, verbose=False):
    """Opens a problem description in the default browser.

    Parameters
    ----------
    problem_id: str
        A string representing the problem id
    verbose: bool
        A boolean flag to enable verbose mode
    Returns:
    -------
    None
    """
    # use problem rating to check if problem exists
    problem_rating = get_problem_rating(problem_id, verbose)
    if not problem_rating:
        print(f"Invalid problem ID: {problem_id}")
        print("Aborting...")
        sys.exit(1)
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


def get_problem_samples(problem_id: str, verbose=False) -> bytes:
    """Downloads the sample files for a problem

    Parameters
    ----------
    problem_id: str
        A string representing the problem id
    verbose: bool
        A boolean flag to enable verbose mode

    Returns
    -------
    bytes
        A bytestring with the contents of the zip file
    """
    if verbose:
        print(
            f"Making http request: https://open.kattis.com/problems/{problem_id}/file/statement/samples.zip")
    r = requests.get(
        f"https://open.kattis.com/problems/{problem_id}/file/statement/samples.zip")
    # bad request
    if r.status_code != 200:
        print(f"URL {r.url} returned non 200 status")
        print("Aborting...")
        sys.exit(1)
    # download and write zip file
    print("Sample files found! Returning content.") if verbose else None
    return r.content
