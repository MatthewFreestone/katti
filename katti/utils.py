import os
import re

# supported programming languages
SUPPORTED_LANGS = {
    "cpp": ".cpp",
    "c++": ".cpp",
    "java": ".java",
    "python": ".py"
}
# convert an extension to a submission language
EXTENSION_TO_LANG = {
    ".cpp": "C++",
    ".java": "Java",
    ".py": "Python"
}

JUNK_EXTENSIONS = {
    "class",
    "exe",
    "out",
    "o",
}


def get_source_extension(problem_id: str) -> str:
    """Helper function to get the extension of the source file for a problem.

    Parameters:
    -----------
    problem_id: str
        The id of the problem to get the source file for

    Returns:
    --------
    A string representing the extension of the source file
    """
    for f in os.listdir():
        base, extension = os.path.splitext(os.path.basename(f))
        if base == problem_id and extension in EXTENSION_TO_LANG:
            return extension
    print("No suitable source files found")
    print("Currently Supported Extensions: " +
          ", ".join(EXTENSION_TO_LANG.keys()))
    print("Aborting...")
    raise Exception("No suitable source files found")


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
