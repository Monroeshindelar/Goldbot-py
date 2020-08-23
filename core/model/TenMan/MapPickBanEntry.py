from core.model.TenMan.TeamStatus import TeamStatus
from core.model.TenMan.PickBanMode import PickBanMode


class MapPickBanEntry:
    def __init__(self, pick_ban_entry: str):
        deconstructed = pick_ban_entry.split("~")
        self.__mode = PickBanMode.get(deconstructed[0])
        self.__team_status = TeamStatus.get(deconstructed[1])

    def get_mode(self) -> PickBanMode:
        return self.__mode

    def get_team_status(self) -> TeamStatus:
        return self.__team_status
