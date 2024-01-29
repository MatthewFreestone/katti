import sys
import os
import webbrowser
import requests
from requests.cookies import RequestsCookieJar
from bs4 import BeautifulSoup
from katti import configloader
from katti.utils import EXTENSION_TO_LANG, get_source_extension, infer_python_version
from katti.constants import MAX_SUBMISSION_CHECKS


# URLs
_PROBLEMS_ENDING = "/problems/"
_LOGIN_ENDING = "/login"
_SUBMIT_ENDING = "/submit"
_STATUS_ENDING = "/submissions/"
_UNFINISHED_ENDING = "/problems?order=title_link&f_solved=off&f_partial-score=on&f_tried=on&f_untried=on"


_HEADERS = {"User-Agent": "kattis-cli-submit"}


def show_description(problem_id: str, kattis_config: configloader.KattisConfig, verbose=False):
    """Opens a problem description in the default browser.

    Parameters
    ----------
    problem_id: str
        A string representing the problem id
    verbose: bool
        A boolean flag to enable verbose mode
    """
    # use problem rating to check if problem exists
    problem_rating = get_problem_rating(problem_id, kattis_config, verbose)
    if not problem_rating:
        print(f"Invalid problem ID: {problem_id}")
        print("Aborting...")
        sys.exit(1)
    url = f"{kattis_config.url}{_PROBLEMS_ENDING}{problem_id}"
    webbrowser.open(url)


def get_problem_rating(problem_id: str, kattis_config: configloader.KattisConfig, verbose=False) -> float:
    """
    Helper function to get the current rating of problem from Kattis

    Parameters:
    ----------
    problem_id: str
        A string representing the problem id
    kattis_config: configloader.KattisConfig
        A KattisConfig object containing the user's kattis config
    verbose: bool
        A boolean flag to enable verbose mode

    Returns:
    -------
    str
        A string representing the problem rating
    """
    url = f"{kattis_config.url}{_PROBLEMS_ENDING}{problem_id}"
    print(f"Making http request: {url}") if verbose else None
    r = requests.get(f"{url}")
    # bad request
    if r.status_code != 200:
        print(f"URL {r.url} returned non 200 status.")
        print("Aborting...")
        r.raise_for_status()
    print("Parsing html...") if verbose else None
    soup = BeautifulSoup(r.text, 'html.parser')
    results = soup.find('span', class_='difficulty_number')
    if results:
        rating = results.text
        print(
            f"Problem rating for {problem_id}: {rating}") if verbose else None
        return float(rating)
    else:
        print(
            f"Unable to find problem rating for {problem_id}") if verbose else None
        raise ValueError(f"Unable to find problem rating for {problem_id}")


def get_problem_samples(problem_id: str, kattis_config: configloader.KattisConfig, verbose=False) -> bytes:
    """Downloads the sample files for a problem

    Parameters
    ----------
    problem_id: str
        A string representing the problem id
    kattis_config: configloader.KattisConfig
        A KattisConfig object containing the user's kattis config
    verbose: bool
        A boolean flag to enable verbose mode

    Returns
    -------
    bytes
        A bytestring with the contents of the zip file
    """
    url = f"{kattis_config.url}{_PROBLEMS_ENDING}{problem_id}/file/statement/samples.zip"
    if verbose:
        print(
            f"Making http request: {url}")
    r = requests.get(url)
    # bad request
    r.raise_for_status()
    # download and write zip file
    print("Sample files found! Returning content.") if verbose else None
    return r.content


def get_updated_ratings(problems_conf: dict, kattis_config: configloader.KattisConfig, verbose=False):
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
            problem_id, kattis_config, verbose)
    configloader.problem_config_changed()


def add_problem(problem_id: str, problem_conf: dict, kattis_config: configloader.KattisConfig, verbose=False):
    """Adds a problem to the problems config

    Parameters
    ----------
    problem_id: str
        A string representing the problem id
    problem_conf: dict
        A dictionary containing the problems config
    kaatits_config: configloader.KattisConfig
        A KattisConfig object containing the user's kattis config
    verbose: bool
        A boolean flag to enable verbose mode
    """
    # check if problem exists
    old_rating = problem_conf.get(problem_id, None)
    problem_rating = get_problem_rating(problem_id, kattis_config, verbose)
    if not problem_rating:
        print(f"Invalid problem ID: {problem_id}")
        print("Aborting...")
        sys.exit(1)

    if old_rating and old_rating == problem_rating:
        print(
            f"Problem '{problem_id}' already added (rating: {problem_rating}).")
        return
    elif old_rating and old_rating != problem_rating:
        print(
            f"Updated rating of '{problem_id}' from {old_rating} to {problem_rating}.")
    else:
        print(
            f"Adding problem '{problem_id}' to problems config (rating {problem_rating}).")
    # add problem to config
    problem_conf[problem_id] = problem_rating
    configloader.problem_config_changed()

def add_all_unfinished_problems(unsolved_problems_conf: dict, kattis_config: configloader.KattisConfig, verbose=False):
    """Gets all unfinished problems from Kattis
    
    Parameters
    ----------
    kattis_config: configloader.KattisConfig
        A KattisConfig object containing the user's kattis config
    verbose: bool
        A boolean flag to enable verbose mode

    Warning
    ----------
    This function is slow and should only be used to initialize the unsolved problems config
    """

    page_num = 1
    url = f"{kattis_config.url}{_PROBLEMS_ENDING[:-1]}?page={page_num}"

    r = requests.get(url)
    r_content = r.text

    soup = BeautifulSoup(r_content, 'html.parser')
    max_page_num = soup.find_all('div', class_='flex gap-2')[0].find_all('a')[2].text
    max_page_num = int(max_page_num)

    print("Logging in...") if verbose else None
    login_response = login(kattis_config, verbose)

    # for each page of problems
    while page_num <= max_page_num:
        print(f"Getting unsolved problems from page {page_num}...") if verbose else None
        url = f"{kattis_config.url}{_UNFINISHED_ENDING}&page={page_num}"
        r = requests.get(url, cookies=login_response.cookies, headers=_HEADERS)
        r_content = r.text

        soup = BeautifulSoup(r_content, 'html.parser')
        try:
            rows = soup.find_all('tbody')[1].find_all('tr')
        except:
            print('No more problems found') if verbose else None
            break

        # add every problem on the page to unsolved_problems
        for row in rows:
            link = row.find('a', href=True)
            problem_id = link['href'].split('/problems/')[1]
            problem_rating_elem = row.find('span', class_='difficulty_number')

            if problem_rating_elem:
                problem_rating = problem_rating_elem.text
            else:
                problem_rating = 'Difficulty rating not found'

            # convert rating to float if possible
            # for multi-rating problems, keep as string for later parsing
            try:
                problem_rating = float(problem_rating)
            except ValueError:
                problem_rating = problem_rating

            unsolved_problems_conf[problem_id] = problem_rating
            print(f'Added {problem_id} with rating {problem_rating} to unsolved_problems') if verbose else None
        
        page_num += 1
    
    configloader.unsolved_problems_config_changed()


def post(kattis_config: configloader.KattisConfig, user_config: dict, verbose=False):
    """Posts a submission to Kattis

    Parameters
    ----------
    kattis_config: configloader.KattisConfig
        A KattisConfig object containing the user's kattis config
    user_config: configloader.UserConfig
        A UserConfig object containing the user's config
    verbose: bool
        A boolean flag to enable verbose mode
    """

    # TODO: add handling for explict problem id and source file selection
    problem_id = os.path.basename(os.getcwd())
    extension = get_source_extension(problem_id)
    if not extension:
        raise ValueError("No source file found.")
    lang = EXTENSION_TO_LANG.get(extension)

    if not lang:
        raise ValueError("Invalid source file extension.")

    # only needed for Java submissions
    mainclass = problem_id if extension == ".java" else None
    # language to submit as
    if lang == "Python":
        version = infer_python_version(problem_id + extension)
        lang = "Python " + str(version)
    # list of files to submit
    submission_files = [problem_id + extension]
    print(
        f"Submission files: {', '.join(submission_files)}") if verbose else None

    print("Logging in...") if verbose else None
    login_response = login(kattis_config, verbose)

    # TODO: add support for -f flag to skip
    confirm_submission(problem_id, lang, submission_files)

    # try post call
    try:
        submit_response = submit(
            login_response.cookies,
            problem_id,
            lang,
            submission_files,
            kattis_config.url,
            mainclass
        )
    except requests.exceptions.RequestException as e:
        print("Submit Connection Failed:", e)
        sys.exit(0)
    # print submission id message
    plain_text_response = submit_response.content.decode(
        "utf-8").replace("<br />", "\n")
    print(plain_text_response)
    # check the submission acceptance status
    # submission_id = plain_text_response.split()[-1].rstrip(".")
    # webbrowser.open(submission_id)
    # check_submission_status(problem_id + extension, submission_id, kattis_config, user_config, login_response.cookies, verbose)


def login(kattis_config: configloader.KattisConfig, verbose=False) -> requests.Response:
    """
    A helper function to log a user in to kattis

    Parameters
    ----------
    kattis_config: configloader.KattisConfig
        A KattisConfig object containing the user's login credentials

    Returns
    -------
    requests.Response
        A response object containing the response from the login request
    """
    login_creds = {
        "user": kattis_config.username,
        "token": kattis_config.token,
        "script": "true"
    }
    login_url = kattis_config.url + _LOGIN_ENDING
    r = requests.post(login_url, data=login_creds, headers=_HEADERS)

    if r.status_code == 200:
        print("Login Successful") if verbose else None
    else:
        print("Login Failed")
        if r.status_code == 403:
            print("Invalid Username/Token (403)")
        elif r.status_code == 404:
            print("Invalid Login URL (404)")
        else:
            print("Status Code:", r.status_code)
        r.raise_for_status()
    return r


def confirm_submission(problem_id, lang, files):
    """
    A confirmation message for submissions if verbose is set

    Parameters
    ----------
    problem_id: str
        A string representing the problem id
    lang: str
        A string representing the language to submit as
    files: list
        A list of strings representing the files to submit
    """
    print("Problem: ", problem_id)
    print("Language: ", lang)
    print("Files: ", ", ".join(files))
    print("Submit [y/N]: ", end="")
    answer = input()
    if not answer or answer.lower() not in ["y", "yes"]:
        print("Aborting...")
        sys.exit(0)
    print()


def submit(cookies: RequestsCookieJar, problem_id: str, lang: str, files: list[str], url: str, mainclass: str | None = "", verbose=False) -> requests.Response:
    """
    A helper function to post a solution to kattis

    Parameters
    ----------
    cookies: requests.cookies.RequestsCookieJar
        A cookie object containing the cookies from the login request
    problem_id: str
        A string representing the problem id
    lang: str
        A string representing the language to submit as
    files: list
        A list of strings representing the files to submit
    url: str
        A string representing the url to submit to
    mainclass: str
        A string representing the mainclass to submit as
    verbose: bool
        A boolean flag to enable verbose mode

    Returns
    -------
    requests.Response
        A response object containing the response from the submit request
    """
    data = {
        "submit": "true",
        "submit_ctr": 2,
        "language": lang,
        "mainclass": mainclass,
        "problem": problem_id,
        "tag": "",
        "script": "true"
    }
    submission_files = []
    for i in files:
        with open(i) as f:
            submission_files.append(
                (
                    "sub_file[]",
                    (
                        os.path.basename(i),
                        f.read(),
                        "application/octet-stream"
                    )
                )
            )
    submit_url = url + _SUBMIT_ENDING
    r = requests.post(submit_url, data=data,
                      files=submission_files, cookies=cookies, headers=_HEADERS)
    status = r.status_code
    if status == 200 and verbose:
        print("Submission Status: 200\n")
    elif status != 200:
        print("Submit Failed")
        if verbose:
            if status == 403:
                print("Access Denied (403)")
            elif status == 404:
                print("Invalid Submission URL (404)")
            else:
                print("Status Code:", status)
        r.raise_for_status()
    return r

