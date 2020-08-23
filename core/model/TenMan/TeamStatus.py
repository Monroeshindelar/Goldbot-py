from enum import Enum


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
            raise SyntaxError

    @staticmethod
    def to_string(status: "TeamStatus") -> str:
        if status == TeamStatus.A:
            return "A"
        elif status == TeamStatus.B:
            return "B"

