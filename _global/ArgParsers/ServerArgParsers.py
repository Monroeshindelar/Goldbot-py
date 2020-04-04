from _global.ArgParsers.ThrowingArgumentParser import ThrowingArgumentParser


class ServerArgParsers:
    LEADERBOARD_ARG_PARSER = ThrowingArgumentParser(add_help=False)
    LEADERBOARD_ARG_PARSER.add_argument("-m", "--mobile", action="store_true")
    LEADERBOARD_ARG_PARSER.add_argument("-t", "--top")
    LEADERBOARD_ARG_PARSER.add_argument("-s", "--sort")
    LEADERBOARD_ARG_PARSER.add_argument("emoji")
