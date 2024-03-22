import pkg_resources
import os
from katti import webkattis, configloader, localproblems, parser
from katti.constants import colors

USER_CONF_PATH = pkg_resources.resource_filename(__name__, 'user_config.json')
PROBLEMS_CONF_PATH = pkg_resources.resource_filename(
    __name__, 'problem_ids.json')
UNSOLVED_PROBLEMS_CONF_PATH = pkg_resources.resource_filename(
    __name__, 'unsolved_problems.json')
SELECTED_PROBLEMS_CONF_PATH = pkg_resources.resource_filename(
    __name__, 'selected_ids.json')
KATTIS_CONF_PATH = os.path.join(os.path.expanduser('~'), '.kattisrc')

def main():
    # TODO these 4 operations are potentially blocking, consider moving to separate threads
    user_conf = configloader.load_user_config(USER_CONF_PATH)
    problems_conf = configloader.load_problems_config(PROBLEMS_CONF_PATH)
    unsolved_problems_conf = configloader.load_unsolved_problems_config(UNSOLVED_PROBLEMS_CONF_PATH)
    selected_problems_conf = configloader.load_selected_problems_config(SELECTED_PROBLEMS_CONF_PATH)
    kattis_conf = configloader.get_kattis_config(KATTIS_CONF_PATH)

    # add command line args
    arg_parser = parser.get_parser()
    args = arg_parser.parse_args()
    # track verbosity
    verbose = args.verbose

    # handle args passed in
    cmd = args.subcommand

    if cmd == "get" or cmd == "g":
        problem_id = args.get
        preferred_language = user_conf.get("preferred_language", None)
        localproblems.get_problem(
            problem_id, problems_conf, kattis_conf, preferred_language, verbose=verbose)
    elif cmd == "random":
        # defaults to -1 if not specified
        rating = args.random
        localproblems.get_random_problem(
            rating, user_conf, unsolved_problems_conf, kattis_conf, verbose=verbose)
    elif cmd == "selected" or cmd == "sel":
        # defaults to -1 if not specified
        rating = args.selected
        localproblems.get_random_problem(
            rating, user_conf, selected_problems_conf, kattis_conf, verbose=verbose)
    elif cmd == "run" or cmd == "r":
        localproblems.run(problems_conf, verbose=verbose)
    elif cmd == "submit" or cmd == "s":
        filename = args.submit
        webkattis.post(kattis_conf, user_conf, filename=filename, verbose=verbose)
    elif cmd == "add" or cmd == "a":
        problem_id = args.add
        webkattis.add_problem(problem_id, problems_conf,
                            kattis_conf, verbose=verbose)
    elif cmd == "description" or cmd == "d":
        problem_id = args.description
        webkattis.show_description(problem_id, kattis_conf, verbose=verbose)
    elif cmd == "update" or cmd == "u":
        localproblems.update(
            user_conf, problems_conf, unsolved_problems_conf, kattis_conf, verbose=verbose)
    else:
        print(args)
        arg_parser.print_help()

    # update conf files if needed
    configloader.save_user_config(USER_CONF_PATH, user_conf)
    configloader.save_problems_config(PROBLEMS_CONF_PATH, problems_conf)
    configloader.save_unsolved_problems_config(UNSOLVED_PROBLEMS_CONF_PATH, unsolved_problems_conf)



if __name__ == "__main__":
    main()
