from enum import Enum


class Game(Enum):
    CSGO = 0,
    VALORANT = 1

    @staticmethod
    def get(g):
        g = g.lower()
        if g == "csgo" or g == "cs:go" or g == "counter strike" or g == "global offensive" \
                or g == "counter strike global offensive" or g == "counter strike: global offensive":
            return Game.CSGO
        elif g == "valorant":
            return Game.VALORANT
