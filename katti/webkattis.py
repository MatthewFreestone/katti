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
    """
    # use problem rating to check if problem exists
    problem_rating = get_problem_rating(problem_id, verbose)
    if not problem_rating:
        print(f"Invalid problem ID: {problem_id}")
        print("Aborting...")
        sys.exit(1)
    webbrowser.open("https://open.kattis.com/problems/" + problem_id)


def get_problem_rating(problem_id: str, verbose=False) -> float:
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
    return float(rating)


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

def get_updated_ratings(problems_conf: dict, verbose=False):
    """Updates the problem ratings in the problems config

    Parameters
    ----------
    problems_conf: dict
        A dictionary containing the problems config
    verbose: bool
        A boolean flag to enable verbose mode
    """
    # TODO: add a timeout
    # TODO: add multithreading
    print("Updating problem ratings...") if verbose else None
    for problem_id in problems_conf:
        problems_conf[problem_id] = get_problem_rating(
            problem_id, verbose)
    configloader.problem_config_changed()

def add_problem(problem_id: str, problem_conf: dict, verbose=False):
    """Adds a problem to the problems config

    Parameters
    ----------
    problem_id: str
        A string representing the problem id
    problem_conf: dict
        A dictionary containing the problems config
    verbose: bool
        A boolean flag to enable verbose mode
    """
    # check if problem exists
    old_rating = problem_conf.get(problem_id, None)
    problem_rating = get_problem_rating(problem_id, verbose)
    if not problem_rating:
        print(f"Invalid problem ID: {problem_id}")
        print("Aborting...")
        sys.exit(1)

    if old_rating and old_rating == problem_rating:
        print(f"Problem '{problem_id}' already added (rating: {problem_rating}).")
        return
    elif old_rating and old_rating != problem_rating:
        print(f"Updated rating of '{problem_id}' from {old_rating} to {problem_rating}.")
    else:
        print(f"Adding problem '{problem_id}' to problems config (rating {problem_rating}).")
    # add problem to config
    problem_conf[problem_id] = problem_rating
    configloader.problem_config_changed()

def post(kattis_config, verbose=False):
    config = get_config()
    problem_id = os.path.basename(os.getcwd())
    extension = get_source_extension(problem_id)
    lang = _extension_to_lang.get(extension)
    # only needed for Java submissions
    mainclass = problem_id if extension == ".java" else None
    # language to submit as
    if lang == "Python":
        version = determine_python_version(problem_id + extension)
        lang = "Python " + str(version)
    # list of files to submit
    submission_files = [problem_id + extension]
    try:
        login_response = login(config)
    except requests.exceptions.RequestException as e:
        print("Login Connection Failed:", e)
        sys.exit(0)
    report_login_status(login_response)
    confirm_submission(problem_id, lang, submission_files)
    # try post call
    try:
        submit_response = submit(
        login_response.cookies,
        problem_id,
        lang,
        submission_files,
        mainclass
        )
    except requests.exceptions.RequestException as e:
        print("Submit Connection Failed:", e)
        sys.exit(0)
    report_submission_status(submit_response)
    # print submission id message
    plain_text_response = submit_response.content.decode("utf-8").replace("<br />", "\n")
    print(plain_text_response)
    # check the submission acceptance status
    submission_id = plain_text_response.split()[-1].rstrip(".")
    check_submission_status(problem_id + extension, submission_id)

"""
A helper functiont to log a user in to kattis
Params: A ConfigParser object config
Returns: A requests object
"""
def login(config):
  username, token = parse_config(config)
  login_creds = {
    "user": username,
    "token": token,
    "script": "true"
  }
  return requests.post(_LOGIN_URL, data=login_creds, headers=_HEADERS)


def parse_config(config):
    """
    Helper function for login. Parses a config file for username and submit token.
    On failure to parse config file, exits control flow
    Params: A ConfigParser object
    Returns: A tuple of username and token
    """
    username = config.get("user", "username")
    token = None
    try:
        token = config.get("user", "token")
    except configparser.NoOptionError:
        pass
    if token is None:
        print("Corrupted .katisrc file")
        print("Please navigate to https://open.kattis.com/help/submit and download a new .kattisrc")
        print("Aborting...")
        sys.exit(0)
    return (username, token)