from katti import configloader
from katti import webkattis
import random
import os
import sys
from zipfile import ZipFile
from datetime import datetime

# supported programming languages
_suported_langs = {
    "cpp": ".cpp",
    "c++": ".cpp",
    "java": ".java",
    "python": ".py"
}
# convert an extension to a submission language
_extension_to_lang = {
    ".cpp": "C++",
    ".java": "Java",
    ".py": "Python"
}


def get_boilerplate(problem_id: str, rating: str, extension: str) -> tuple[str, str]:
    """Gives filename and boilerplate code for a problem in a given programming language.

    Parameters:
    ----------
    problem_id: str
        A string representing the problem id
    rating: str
        A string representing the problem rating
    extension: str
        A string representing the file extension

    Returns:
    -------
    tuple[str,str]
        A tuple containing the filename and the boilerplate code
    """
    # c++ boilerplate
    content = None
    if extension == ".cpp":
        filename = problem_id + extension
        content =\
            """\
/*
Rating: ~ %s / 10
Link: https://open.kattis.com/problems/%s
*/

#include <iostream>
#include <string>
#include <vector>
using namespace std;

typedef long long ll;

void fast() {
  ios_base::sync_with_stdio(false);
  cin.tie(NULL);
}

int main() {
  return 0;
}
""" % (rating, problem_id)

  # java boilerplate
    elif extension == ".java":
        capitalized_problem_id = problem_id[0].upper() + problem_id[1:].lower()
        filename = capitalized_problem_id + extension
        content =\
            """\
/*
Rating: ~ %s / 10
Link: https://open.kattis.com/problems/%s
*/

import java.io.*;
import java.util.*;

public class %s {
  static BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

  public static void main(String[] args) {
  }
}
""" % (rating, problem_id, capitalized_problem_id)

    # python boilerplate
    elif extension == ".py":
        filename = problem_id + extension
        content =\
            """\
# Rating: ~ %s / 10
# Link: https://open.kattis.com/problems/%s

def main():

if __name__ == "__main__":
  main()
""" % (rating, problem_id)

    return (filename, content)


def get_problem(problem_id, problems_config, preferred_language=None, verbose=False):
    """
    Creates a directory with the problem id, test cases, and boilerplate code for a given problem id.

    Parameters
    ----------
    problem_id: str
        A string representing the problem id
    preferred_language: str
        A string representing the preferred programming language
        Options: "cpp", "c++", "java", "python"
    """

    # get problem rating, will exit if problem id is invalid
    rating = webkattis.get_problem_rating(problem_id, verbose=verbose)

    # get programming language and extension
    extension = None
    input_string = "Programming Language: " if preferred_language is None else f"Programming Language [{preferred_language}]: "
    while True:
        language = input(input_string).lower()
        if language == "" and preferred_language is not None:
            extension = _suported_langs[preferred_language]
            break
        if language in _suported_langs:
            extension = _suported_langs[language]
            break
        print(f'Language "{language}" not suported...')

    samples = webkattis.get_problem_samples(problem_id, verbose=verbose)

    # write problem id and rating to config file
    if problem_id not in problems_config:
        problems_config[problem_id] = rating
        configloader.problem_config_changed()

    # write content into a zip file
    with open("samples.zip", mode="wb") as f:
        f.write(samples)
        f.close()

    # create the directory, unzip the samples, remove the zip file, create the boilerplate file
    if not os.path.exists(problem_id):
        print(f"Creating directory {problem_id} ...") if verbose else None
        os.mkdir(problem_id)
    else:
        print(f"Directory {problem_id} already exists...") if verbose else None
    print("Unzipping samples...") if verbose else None
    with ZipFile("samples.zip", 'r') as zipObj:
        zipObj.extractall(path=problem_id)

    print("Removing zip file...") if verbose else None
    os.remove("samples.zip")
    # os.system("rm -iv samples.zip")
    os.chdir(problem_id)
    filename, boilerplate = get_boilerplate(problem_id, rating, extension)
    if not os.path.exists(filename):
        print(
            f"Writing boilerplate file {problem_id}{extension} ...") if verbose else None
        with open(filename, mode="w") as f:
            f.write(boilerplate)
            f.close()
    else:
        print(
            f"File {filename} already exists, skipping writing boilerplate...") if verbose else None

    if input('Open in browser? [Y/n]: ').lower() not in {'n', 'no'}:
        webkattis.show_description(problem_id, verbose=verbose)
    os.chdir("..")

def get_random_problem(rating: str, user_conf: dict, problems_conf: dict, verbose: bool = False) -> None:
    """Gets a random problem from the list of unsolved problems within the given rating range.

    Parameters
    ----------
    rating: str
        A string desired rating 
    user_conf: dict
        A dictionary representing the user configuration
    problems_conf: dict
        A dictionary representing the problems configuration
    verbose: bool
        A boolean representing whether or not to print verbose output
    """
    invalid = False
    try:
        rating = int(rating)
    except:
        invalid = True
    if invalid or not 1 <= rating <= 10:
        print("Invalid rating. Rating must be a valid integer between 1 and 10")
        print("Aborting...")
        sys.exit(1)
    # update ratings if necessary
    prev_update = datetime.strptime(user_conf["ids_last_updated"], "%Y-%m-%d %H:%M:%S.%f")
    print(f"Ratings last updated on {prev_update}") if verbose else None
    current = datetime.now()
    # 3600 seconds in hour - no hours field
    hours = (current - prev_update).total_seconds() / 3600
    if hours >= user_conf["ratings_update_period"]:
        print("Updating ratings...") if verbose else None
        webkattis.get_updated_ratings(problems_conf, verbose=verbose)
        user_conf["ids_last_updated"] = str(current)
        configloader.user_config_changed()
    else:
        print(f"Ratings updated {hours: .2f} hours ago. Skipping update...") if verbose else None

    # will hold all unsolved problems within the range
    choices = set()
    solved = set([i.split(".")[0] for i in user_conf["solved"]])
    for problem, val in problems_conf.items():
        if  rating <= val < (rating + 1):
            choices.add(problem)
    choices -= solved
    print(f"Found {len(choices)} unsolved problems rated {rating}") if verbose else None
    if choices:
        pick = random.choice(list(choices))
        print(f"{pick}: {problems_conf[pick]}")
        if input('Open in browser? [Y/n]: ').lower() not in {'n', 'no'}:
            webkattis.show_description(pick, verbose=verbose)
        return
    print("It appears you have solved all problems rated %.1f - %.1f" % (rating, rating + 0.9))