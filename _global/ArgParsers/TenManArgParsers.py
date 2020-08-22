from _global.ArgParsers.ThrowingArgumentParser import ThrowingArgumentParser


class TenManArgParsers:
    TM_INIT_ARG_PARSER = ThrowingArgumentParser(add_help=False)
    TM_INIT_ARG_PARSER.add_argument("-h", "--help", action="store_true")
    TM_INIT_ARG_PARSER.add_argument("game")

