from katti import configloader
from katti import webkattis
import random
import os
import sys
from zipfile import ZipFile
from datetime import datetime
from typing import List, Tuple
import re
import filecmp
import subprocess

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

_junk_extensions = {
    "class",
    "exe",
    "out",
    "o",
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

def run(problems_conf, verbose: bool = False) -> None:
    """ Runs all the sample inputs for a given kattis problem and checks them for
    basic correctness (does not check relative error)

    Parameters:
    -----------
    verbose: bool
        A boolean representing whether or not to print verbose output
    """
    file_name = os.path.basename(os.getcwd())
    if file_name not in problems_conf:
        print("Current directory does not match a problem id")
        print("Please cd into the directory of the problem you want to test")
        sys.exit(1)
    # find which language to use
    extension = get_source_extension(file_name, verbose=verbose)
    samples, answers = get_samples_and_answers(verbose=verbose)
    executable = run_compiler(file_name, extension, verbose=verbose)
    if executable is not None:
        if samples and answers:
            run_test_cases(executable, samples, answers, verbose=verbose)
        else:
            print("No sample inputs and answers found")
            print("Aborting...")
    else:
        print("No executable found")
        print("Aborting...")

def get_source_extension(problem_id, verbose: bool = False, specific_file: str = None):
    """Helper function to find a problem's sorce file extension

    Parameters:
    -----------
    problem_id: str
        A string representing the problem id
    verbose: bool
        A boolean representing whether or not to print verbose output
    """
    if specific_file is not None:
        base, extension = os.path.splitext(os.path.basename(specific_file))
        if base == problem_id and extension in _extension_to_lang:
            return extension
        else:
            print(f"File {specific_file} is not a valid source file")
            print("Aborting...")
            sys.exit(1)

    for f in os.listdir():
        base, extension = os.path.splitext(os.path.basename(f))
        if base == problem_id and extension in _extension_to_lang:
            print(f"Found source file {f}") if verbose else None
            return extension
    print("No suitable source files found")
    print(f"Currently Supported Extensions: {_extension_to_lang.keys()}")
    print("Aborting...")
    sys.exit(1)

def get_samples_and_answers(verbose: bool = False) -> Tuple[List[str], List[str]]:
    """Helper function to get sample inputs and outputs for comparison

    Parameters:
    -----------
    verbose: bool
        A boolean representing whether or not to print verbose output

    Returns:
    --------
    A tuple of two lists, the first containing the names sample input files and the second
    containing the names of the sample output files

    """
    samples = []
    answers = []
    for f in os.listdir():
        _, extension = os.path.splitext(os.path.basename(f))
        if extension == ".in":
            samples.append(f)
        if extension == ".ans":
            answers.append(f)
    print(f"Found {len(samples)} sample inputs and {len(answers)} sample outputs") if verbose else None
    return (samples, answers)


def run_compiler(file_name: str, extension: str, verbose = False) -> str:
    """Helper function for run() method. Compiles the code for compiled languages and checks
    existence of interpreter for interpreted languages

    Parameters:
    ----------
    file_name: str
        A string representing the name of the source file
    extension: str
        A string representing the extension of the source file
    verbose: bool
        A boolean representing whether or not to print verbose output

    Returns:
    --------
    A string representing a system call to run the source code, or None on failure
    """
    status = 1
    if extension == ".cpp":
        # check presence of g++ compiler
        # status = os.system("which g++")
        status = subprocess.run(['g++', '--version'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if status != 0:
            print("Unable to locate g++ compiler")
            print("Aborting...")
            return None
        # compile the code
        print("Compiling %s..." % (file_name + extension)) if verbose else None
        os.system("g++ -std=c++11 %s" % (file_name + extension))
        return "./a.out"
    if extension == ".java":
        # check existence of javac compiler
        status = os.system("which javac")
        if status != 0:
            print("Unable to locate javac compiler")
            print("Aborting...")
            return None
        # compile the code
        print("Compiling %s..." % (file_name + extension)) if verbose else None
        os.system("javac %s" % (file_name + extension))
        return "java " + file_name
    if extension == ".py":
        print("Trying to infer Python version...") if verbose else None
        version = infer_python_version(file_name + extension)
        print("Python version inferred as %d" % version) if verbose else None
        python_warning = '''
        NOTE: Katti only uses the aliases 'python2', 'python3', and 'python' for python interpreters
        Please make sure the appropriate aliases are in your PATH environment variable
        Aborting...
        '''
        if version == 2:
            status = os.system("which python2")
            if status != 0:
                print("Unable to locate Python 2 interpreter")
                print(python_warning)
                return None
            return "python2 " + file_name + extension
        else:
            result = subprocess.run(['python3', '--version'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            status = result.returncode
            if status != 0:
                print("python3 alias failed, trying python") if verbose else None
                result = subprocess.run(['python', '--version'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                status = result.returncode
                if status != 0:
                    print("Unable to locate Python 3 interpreter")
                    print(python_warning)
                    return None
                else:
                    return "python " + file_name + extension
            return "python3 " + file_name + extension


def run_test_cases(executable: str, sample_files: List[str], expected: List[str], verbose=False):
    """Runs a given kattis problem through the provided sample inputs. Assumes
    code is already compiled

    Parameters:
    -----------
    executable: str
        A string representing a system call to run the source code
    sample_files: List[str]
        A list of strings representing the names of the sample input files
    expected: List[str]
        A list of strings representing the names of the sample output files
    verbose: bool
        A boolean representing whether or not to print verbose output
    """
    print("Running test cases...") if verbose else None
    for i, sample in enumerate(sample_files):
        fail = False
        # get rid of .in extension in order to match with corresponding .ans file
        base = '.'.join(sample.split('.')[:-1])
        executable += " < " +  sample + " > test.out"
        os.system(executable)

        # replace crlf with lf
        with open("test.out", mode="r", newline="\r\n") as f:
            lines = f.readlines()
        f.close()
        with open("test.out", mode="w", newline="\n") as f:
            for line in lines:
                f.write(line.replace("\r\n", "\n"))
        f.close()

        files_equal = filecmp.cmp("test.out", base + ".ans", shallow=False)
        # status = os.system("diff test.out %s.ans" % base)
        # if status != 0:
        if not files_equal:
            if verbose:
                print("FAIL on sample input %s" % sample)
                print("<<< Expected Output >>>")
                with open(base + ".ans", mode="r") as f:
                    print(f.read())
                f.close()
                print("<<< Actual Output >>>")
                with open("test.out", mode="r") as f:
                    print(f.read())
                f.close()
            else:
                print("-", end="")
        else:
            if verbose:
                print("PASS on sample input: %s" % sample)
            else:
                print("+", end="")
        os.remove("test.out")
        # os.system("rm *.out")
    cleanup_after_run(verbose)
    # formatting
    print()

def cleanup_after_run(verbose=False):
    """Cleans up after a run() call by removing all compiled files

    Parameters:
    -----------
    verbose: bool
        A boolean representing whether or not to print verbose output
    """
    if verbose:
        print("Cleaning up...") 
    all_files = [item.split('.') for item in os.listdir()]
    for *item, extension in all_files:
        item = '.'.join(item)
        if extension in _junk_extensions:
            print("Removing %s.%s" % (item, extension)) if verbose else None
            os.remove(item + "." + extension)
    if verbose:
        print("Done cleaning up")


def infer_python_version(filename) -> int:
    """Helper function to determine if a python file is python2 or python3. Taken from kattis's submit.py

    Parameters:
    -----------
    file_name: str
        The name of the file to check
    
    Returns:
    --------
    An integer representing the python version of the file, 2 or 3
    """
    python2 = re.compile(r'^\s*\bprint\b *[^ \(\),\]]|\braw_input\b')
    with open(filename) as f:
        for index, line in enumerate(f):
            if index == 0 and line.startswith('#!'):
                if 'python2' in line:
                    return 2
                if 'python3' in line:
                    return 3
            if python2.search(line.split('#')[0]):
                return 2
    return 3
