from enum import Enum


class PairStatus(Enum):
    INCOMPLETE = 0
    UNASSIGNED = 1
    BOXED = 2
    TEAM = 3
    DEAD = 4
