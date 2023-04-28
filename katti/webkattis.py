import sys
import os
import webbrowser
import requests
import re
import datetime
import bisect
import time
from bs4 import BeautifulSoup
from katti import configloader
from katti.utils import EXTENSION_TO_LANG, get_source_extension, infer_python_version
from katti.constants import MAX_SUBMISSION_CHECKS

# URLs
_LOGIN_ENDING = "/login"
_SUBMIT_ENDING = "/submit"
_STATUS_ENDING = "/submissions/"

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

def post(kattis_config: configloader.KattisConfig, user_config, verbose=False):
    problem_id = os.path.basename(os.getcwd())
    extension = get_source_extension(problem_id)
    if not extension:
        sys.exit(1)
    lang = EXTENSION_TO_LANG.get(extension)
    # only needed for Java submissions
    mainclass = problem_id if extension == ".java" else None
    # language to submit as
    if lang == "Python":
        version = infer_python_version(problem_id + extension)
        lang = "Python " + str(version)
    # list of files to submit
    submission_files = [problem_id + extension]
    print(f"Submission files: {', '.join(submission_files)}") if verbose else None

    print("Logging in...") if verbose else None
    try:
        login_response = login(kattis_config)
    except requests.exceptions.RequestException as e:
        print("Login Connection Failed:", e)
        sys.exit(0)
    report_login_status(login_response, verbose)
    confirm_submission(problem_id, lang, submission_files) if verbose else None
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
    report_submission_status(submit_response, verbose)
    # print submission id message
    plain_text_response = submit_response.content.decode("utf-8").replace("<br />", "\n")
    print(plain_text_response)
    # check the submission acceptance status
    submission_id = plain_text_response.split()[-1].rstrip(".")
    check_submission_status(problem_id + extension, submission_id, kattis_config, user_config, verbose)

def login(kattis_config: configloader.KattisConfig):
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
    login_url = "https://" + kattis_config.url + _LOGIN_ENDING
    return requests.post(login_url, data=login_creds, headers=_HEADERS)

def report_login_status(response: requests.Response, verbose=False):
    """
    A helper function to report the status of a login request

    Parameters
    ----------
    response: requests.Response
        A response object containing the response from the login request
    verbose: bool

    Returns
    -------
    None
    """
    status = response.status_code
    if status == 200 and verbose:
        print("Login Status: 200\n")
        return
    elif status != 200:
        print("Login Failed")
        if verbose:
            if status == 403:
                print("Invalid Username/Token (403)")
            elif status == 404:
                print("Invalid Login URL (404)")
            else:
                print("Status Code:", status)
        sys.exit(1)

"""
A confirmation message for submissions if verbose is set

Params: A string problem_id, a string lang, a list files
Returns: None
"""
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
    print("Problem:", problem_id)
    print("Language:", lang)
    print("Files:", ", ".join(files))
    print("Submit (Y/N): ", end="")
    if input()[0].lower() != "y":
        print("Aborting...")
        sys.exit(0)
    print()


"""
Helper function to post a solution to kattis

Params: A requests cookies object for login, a string problem_id,
        a string lang, a list files, a string mainclass
Returns: A post request object
"""
def submit(cookies, problem_id, lang, files, url, mainclass=""):
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
    submit_url = "https://" + url + _SUBMIT_ENDING
    return requests.post(submit_url, data=data, files=submission_files, cookies=cookies, headers=_HEADERS)

def report_submission_status(response, verbose=False):
  status = response.status_code
  if status == 200 and verbose:
    print("Submission Status: 200\n")
    return
  elif status != 200:
    print("Submit Failed")
    if verbose:
      if status == 403:
        print("Access Denied (403)")
      elif status == 404:
        print("Invalid Submission URL (404)")
      else:
        print("Status Code:", status)
    sys.exit(0)



"""
Checks the status of a given submission for acceptance, TLE, etc.

Params: A string submission_file, a string submission_id
Returns: None
"""
def check_submission_status(submission_file, submission_id, kattis_config, user_config, verbose=False):
  global modified
  print("Awaiting result...\n")
  config = kattis_config
  # login
  try:
    login_response = login(config)
  except requests.exceptions.RequestException as e:
    print("Login Connection Failed:", e)
    sys.exit(0)
  # limit number of http requests for a submissions status
  i = 0
  while i < MAX_SUBMISSION_CHECKS:
    response = requests.get(
      "https://" + kattis_config.url + _STATUS_ENDING + submission_id,
      cookies=login_response.cookies,
      headers=_HEADERS
    )
    # parse html for accepted test cases
    soup = BeautifulSoup(response.content, "html.parser")
    status = soup.find("td", class_=re.compile("status"))
    if status:
      child = status.findChildren("span")[0]
      status = set(child["class"])
      runtime = soup.find("td", class_=re.compile("runtime"))
      # success
      if "accepted" in status:
        accepted = soup.find_all("span", class_=re.compile("accepted"))
        # limit length of output
        if len(accepted) > 47:
          print("Test Cases: "
                + ("+" * 47)
                + " plus "
                + str(len(accepted) - 47)
                + " more"
          )
        else:
          print("Test Cases: " + ("+" * len(accepted)))
        print("PASSED")
        print("Runtime: %s" % runtime.text)
        # insert problem into solved section of conf file in sorted order
        bin_search_index = bisect(user_config["solved"], submission_file)
        if user_config["solved"][bin_search_index-1] != submission_file:
          user_config["solved"].insert(bin_search_index, submission_file)
        modified = True
        break
      # failure
      elif "rejected" in status:
        accepted = soup.find_all("span", class_=re.compile("accepted"))
        reason = soup.find("span", class_="rejected")
        cases = soup.find_all("span", title=re.compile("Test case"))
        num_cases = 0
        # find how many test cases passed and which one failed
        if cases:
          num_cases = cases[0]["title"]
          num_cases = re.findall("[0-9]+/[0-9]+", num_cases)
          num_cases = num_cases[0].split("/")[-1]
          # limit output length
          if len(accepted) > 46:
            print("Test Cases: " + ("+" * 44) + "...")
          else:
            print("Test Cases: " + ("+" * len(accepted)) + "-")
        print("FAILED")
        print("Reason:", reason.text)
        if num_cases == 0:
          print("Failed Test Case: N/A")
        else:
          print("Failed Test Case: %i/%s" % (len(accepted)+1, num_cases))
        print("Runtime: %s" % runtime.text)
        break
      # still running
      else:
        accepted = soup.find_all("span", class_=re.compile("accepted"))
        # update output
        if len(accepted) > 47:
          print("Test Cases: "
                + ("+" * 47)
                + " plus "
                + str(len(accepted) - 47)
                + " more", end='\r'
          )
        else:
          print("Test Cases: " + ("+" * len(accepted)), end='\r')
        time.sleep(0.5)
        i += 1
  # add to submission history
  dt = str(datetime.now()).split(".")[0]
  user_config["history"].insert(0, dt + " " + submission_file)
  # truncate submission history to user config history size
  while len(user_config["history"]) > user_config["history_size"]:
    user_config["history"].pop()
  modified = True
