from core.model.tenman.Team import Team
from core.model.tenman.TeamStatus import TeamStatus
from typing import Tuple


class TeamsManager:
    def __init__(self, captain_a: int, captain_b: int):
        self.__team_a = Team(TeamStatus.A, captain_a)
        self.__team_b = Team(TeamStatus.B, captain_b)

    def get_team_status_from_captain(self, captain_id: int) -> TeamStatus:
        if self.__team_a.is_captain(captain_id):
            return self.__team_a.get_status()
        elif self.__team_b.is_captain(captain_id):
            return self.__team_b.get_status()
        else:
            raise SyntaxError

    def add_player(self, player_id: int, team_status: TeamStatus):
        if team_status == TeamStatus.A:
            self.__team_a.add_player(player_id)
        elif team_status == TeamStatus.B:
            self.__team_b.add_player(player_id)

    def get_teams(self) -> Tuple[Team, Team]:
        return self.__team_a, self.__team_b
