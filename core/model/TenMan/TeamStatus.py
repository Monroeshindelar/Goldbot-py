from enum import Enum
from discord.ext.commands import BadArgument


class TeamStatus(Enum):
    A = 0
    B = 1

    @staticmethod
    def get(s: str) -> "TeamStatus":
        s = s.lower()
        if s == "a":
            return TeamStatus.A
        elif s == "b":
            return TeamStatus.B
        else:
            raise BadArgument("Unrecognized team status")
