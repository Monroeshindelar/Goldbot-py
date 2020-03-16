import argparse


class SquadlockeArgParsers:
    SLENCOUNTER_ARG_PARSER = argparse.ArgumentParser()
    SLENCOUNTER_ARG_PARSER.add_argument('-f', action="store_true")
    SLENCOUNTER_ARG_PARSER.add_argument('-s')
    SLENCOUNTER_ARG_PARSER.add_argument('-w')
    SLENCOUNTER_ARG_PARSER.add_argument('-a')
    SLENCOUNTER_ARG_PARSER.add_argument('-all', action="store_true")
    SLENCOUNTER_ARG_PARSER.add_argument('--get-info', action="store_true")
