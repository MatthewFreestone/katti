MAX_SUBMISSION_CHECKS = 10
DEFAULT_RATING_UPDATE_PERIOD = 72
STATUS_MAP = {
    0: 'New', # <invalid value>
    1: 'New',
    2: 'Waiting for compile',
    3: 'Compiling',
    4: 'Waiting for run',
    5: 'Running',
    6: 'Judge Error',
    7: 'Submission Error',
    8: 'Compile Error',
    9: 'Run Time Error',
    10: 'Memory Limit Exceeded',
    11: 'Output Limit Exceeded',
    12: 'Time Limit Exceeded',
    13: 'Illegal Function',
    14: 'Wrong Answer',
    # 15: '<invalid value>',
    16: 'Accepted',
}

class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RED_COLOR = 31
    GREEN_COLOR = 32
