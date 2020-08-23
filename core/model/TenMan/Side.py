from enum import Enum


class Side(Enum):
    CT = 0
    T = 1
    RANDOM = 2

    @staticmethod
    def get(s: str):
        s = s.lower()
        if s == "ct" or s == "defender" or s == "d":
            return Side.CT
        elif s == "t" or s == "attacker" or s == "a":
            return Side.T
        elif s == "r" or s == "random":
            return Side.RANDOM
        else:
            raise SyntaxError
