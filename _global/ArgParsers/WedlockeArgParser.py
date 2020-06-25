from _global.ArgParsers.ThrowingArgumentParser import ThrowingArgumentParser


class WedlockeArgParser:
    WL_INIT_ARG_PARSER = ThrowingArgumentParser(add_help=False)
    WL_INIT_ARG_PARSER.add_argument("-g", "--game")

    WL_ADD_PAIR_ARG_PARSER = ThrowingArgumentParser(add_help=False)
    WL_ADD_PAIR_ARG_PARSER.add_argument("route")
    WL_ADD_PAIR_ARG_PARSER.add_argument("nickname")
    WL_ADD_PAIR_ARG_PARSER.add_argument("gender")
    WL_ADD_PAIR_ARG_PARSER.add_argument("-s", "--species")

    WL_KILL_PAIR_ARG_PARSER = ThrowingArgumentParser(add_help=False)
    WL_KILL_PAIR_ARG_PARSER.add_argument("route")

