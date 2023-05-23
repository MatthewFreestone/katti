import argparse

class Parser(argparse.ArgumentParser):
    def _check_value(self, action, value):
        if action.choices is not None and value not in action.choices:
            raise argparse.ArgumentError(action, "invalid option")
        
def _add_verbose(parser: Parser): 
    parser.add_argument("-v", "--verbose", help="receive verbose outputs", action="store_true")

def get_parser():
    # add command line args
    arg_parser = Parser(
        prog="katti", description="A command line tool testing and submitting kattis problems.")
    subcommands = arg_parser.add_subparsers(title="subcommands", required=True, dest="subcommand")

    get_parser = subcommands.add_parser(
        "get", help="get a kattis problem by its problem id", aliases=["g"])
    _add_verbose(get_parser)
    get_parser.add_argument(
        "get", metavar="<problem-id>", help="get a kattis problem by its problem id", type=str)
    
    run_parser = subcommands.add_parser(
        "run", help="run the test cases for a given problem", aliases=["r"])
    _add_verbose(run_parser)
    
    submit_parser = subcommands.add_parser(
        "submit", help="submit a kattis problem", aliases=["s"])
    _add_verbose(submit_parser)

    description_parser = subcommands.add_parser(
        "description", help="display a problem's description in chrome", aliases=["d"])
    _add_verbose(description_parser)
    description_parser.add_argument(
        "description", metavar="<problem-id>", help="display a problem's description in chrome", type=str)

    add_parser = subcommands.add_parser(
        "add", help="add a problem id to your problem config file", aliases=["a"])
    _add_verbose(add_parser)
    add_parser.add_argument(
        "add", metavar="<problem-id>", help="add a problem id to your problem config file", type=str)

    random_parser = subcommands.add_parser(
        "random", help="selects a random added kattis problem with a given rating")
    _add_verbose(random_parser)
    random_parser.add_argument(
        "random", metavar="<rating>", help="selects a random added kattis problem with a given rating", type=str)
    
    
    return arg_parser
