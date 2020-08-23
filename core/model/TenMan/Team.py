from core.model.TenMan.TeamStatus import TeamStatus
from typing import List


class Team:
    def __init__(self, status: TeamStatus, captain: int):
        self.__status = status
        self.__captain = captain
        self.__players = []
        self.__players.append(captain)

    def get_captain(self) -> int:
        return self.__captain

    def get_status(self) -> TeamStatus:
        return self.__status

    def get_players(self) -> List[int]:
        return self.__players

    def is_captain(self, captain_id: int):
        return captain_id == self.__captain

    def add_player(self, player_id: int):
        if len(self.__players) == 5:
            raise SyntaxError

        self.__players.append(player_id)
