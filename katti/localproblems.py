from katti import configloader
from katti import webkattis
import requests
import os
import sys
from zipfile import ZipFile

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

    Returns
    -------
    None
    """
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

    # get problem rating and samples from kattis
    rating = webkattis.get_problem_rating(problem_id, verbose=verbose)
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
