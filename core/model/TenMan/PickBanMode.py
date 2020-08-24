from enum import Enum
from discord.ext.commands import BadArgument


class PickBanMode(Enum):
    PICK = 0
    BAN = 1

    @staticmethod
    def get(s: str) -> "PickBanMode":
        s = s.lower()
        if s == "p":
            return PickBanMode.PICK
        elif s == "x":
            return PickBanMode.BAN
        else:
            raise BadArgument("Unrecognized pick/ban mode.")
