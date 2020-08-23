from enum import Enum


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
