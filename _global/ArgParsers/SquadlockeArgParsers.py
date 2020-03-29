import argparse


class SquadlockeArgParsers:
    SLENCOUNTER_ARG_PARSER = argparse.ArgumentParser()
    SLENCOUNTER_ARG_PARSER.add_argument("-f", "--fishing", action="store_true")
    SLENCOUNTER_ARG_PARSER.add_argument("-s", "--section")
    SLENCOUNTER_ARG_PARSER.add_argument("-w", "--weather")
    SLENCOUNTER_ARG_PARSER.add_argument("-a", "--area")
    SLENCOUNTER_ARG_PARSER.add_argument("--all", action="store_true")
    SLENCOUNTER_ARG_PARSER.add_argument("--get-info", action="store_true")
    SLENCOUNTER_ARG_PARSER.add_argument("-p", "--public", action="store_true")
