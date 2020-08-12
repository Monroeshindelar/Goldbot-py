from _global.Config import Config
from core.model.TenMan.Game import Game
from core.model.TenMan.CaptainStatus import CaptainStatus
from core.model.TenMan.Side import Side
from typing import Tuple, List
import random


class TenMan:
    def __init__(self, participant_id_list: list, game: Game):
        self.__unselected_participants = participant_id_list
        self.__game = game
        self.__game_type = "bo3"
        if self.__game == Game.CSGO:
            self.__unselected_maps = [m.lower() for m in Config.get_config_property("tenman", "maps", "csgo")]
            self.__map_pick_ban_sequence = Config.get_config_property("tenman", "mapPickBanSequence", "csgo",
                                                                      self.__game_type).split("-")
        elif self.__game == Game.VALORANT:
            self.__unselected_maps = [m.lower() for m in Config.get_config_property("tenman", "maps", "valorant")]
            self.__map_pick_ban_sequence = Config.get_config_property("tenman", "mapPickBanSequence", "valorant",
                                                                      self.__game_type).split("-")
        else:
            raise SyntaxError()

        self.__team_a = []
        self.__team_b = []
        self.__picked_maps = []
        self.__player_pick_sequence = Config.get_config_property("tenman", "playerPickSequence").split("-")
        self.__wait_for_side_pick = False

        if len(self.__player_pick_sequence) < 10 or len(self.__player_pick_sequence) > 10:
            raise SyntaxError

        if self.__player_pick_sequence.count("A") != 5 and self.__player_pick_sequence.count("B") != 5:
            raise SyntaxError

    def get_remaining_participant_ids(self) -> List[str]:
        return self.__unselected_participants

    def get_remaining_maps(self) -> List[str]:
        return [m.capitalize() for m in self.__unselected_maps]

    def set_or_pick_captains(self, captain_ids: List[str]) -> Tuple[str, str]:
        if len(self.__team_a) > 0 or len(self.__team_b) > 0:
            raise SyntaxError

        try:
            self.__unselected_participants.remove(str(captain_ids[0]))
            self.__unselected_participants.remove(str(captain_ids[1]))
        except (TypeError, IndexError):
            captain_ids = []
            for x in range(2):
                index = random.randint(0, len(self.__unselected_participants) - 1)
                captain_ids.append(str(self.__unselected_participants.pop(index)))

        self.__team_a.append(str(captain_ids[0]))
        self.__team_b.append(str(captain_ids[1]))
        return captain_ids[0], captain_ids[1]

    def pick_player(self, player_id: str, captain_id: str) -> Tuple[str, CaptainStatus, str, CaptainStatus]:
        if not self.__captain_turn(captain_id):
            raise SyntaxError

        if len(self.__unselected_participants) == 0:
            raise SyntaxError

        try:
            self.__unselected_participants.remove(str(player_id))
        except ValueError:
            raise SyntaxError

        self.__get_captain_team(captain_id).append(str(player_id))
        self.__player_pick_sequence.pop(0)

        last_pick_id = None
        last_pick_captain_status = None

        if len(self.__unselected_participants) == 1:
            last_pick_captain_status = CaptainStatus.CAPTAIN_A if self.__player_pick_sequence.pop(0) == "A" else CaptainStatus.CAPTAIN_B
            team = self.__team_a if last_pick_captain_status == CaptainStatus.CAPTAIN_A else self.__team_b

            last_pick_id = self.__unselected_participants.pop(0)
            team.append(last_pick_id)

        return player_id, self.__get_captain_status(str(captain_id)), last_pick_id, last_pick_captain_status

    def ban_map(self, map: str, captain_id: str) -> Tuple[CaptainStatus, str]:
        captain_status, decider = self.__map_pick_ban_helper(map, captain_id, True)
        return captain_status, decider

    def pick_map(self, map: str, captain_id: str) -> CaptainStatus:
        captain_status, decider = self.__map_pick_ban_helper(map, captain_id, False)
        self.__picked_maps.append(map)
        self.__wait_for_side_pick = True
        return captain_status

    def pick_side(self, captain_id: str, side: str) -> Tuple[Side, CaptainStatus, str]:
        sequence = self.__map_pick_ban_sequence[0].split("~")

        status = self.__get_captain_status(captain_id)

        if sequence[1] == "A" and not status == CaptainStatus.CAPTAIN_A or sequence[1] == "B" and not status == CaptainStatus.CAPTAIN_B:
            raise SyntaxError

        self.__wait_for_side_pick = False

        decider = None

        if len(self.__map_pick_ban_sequence) == 0:
            index = random.randint(0, len(self.__unselected_maps) - 1)
            decider = self.__unselected_maps.pop(index)
            self.__picked_maps.append(decider)

        return Side.get(side), status, decider

    def __get_captain_status(self, captain_id: str) -> CaptainStatus:
        try:
            if self.__team_a[0] == captain_id:
                return CaptainStatus.CAPTAIN_A
            elif self.__team_b[0] == captain_id:
                return CaptainStatus.CAPTAIN_B
            else:
                return CaptainStatus.NOT_CAPTAIN
        except IndexError:
            return CaptainStatus.NOT_CAPTAIN

    def __captain_turn(self, captain_id: str) -> bool:
        next_pick = self.__player_pick_sequence[0]
        status = self.__get_captain_status(str(captain_id))

        if status is CaptainStatus.NOT_CAPTAIN or (next_pick == "A" and status is not CaptainStatus.CAPTAIN_A) or \
                (next_pick == "B" and status is not CaptainStatus.CAPTAIN_B):
            return False
        else:
            return True

    def __get_captain_team(self, captain_id: str) -> List[str]:
        if self.__get_captain_status(str(captain_id)) == CaptainStatus.CAPTAIN_A:
            return self.__team_a
        elif self.__get_captain_status(str(captain_id)) == CaptainStatus.CAPTAIN_B:
            return self.__team_b
        else:
            raise SyntaxError

    def __map_pick_ban_helper(self, map: str, captain_id: str, is_ban: bool) -> Tuple[CaptainStatus, str]:
        if len(self.__unselected_participants) > 0:
            raise SyntaxError

        if len(self.__map_pick_ban_sequence) == 0:
            raise SyntaxError

        status = self.__get_captain_status(captain_id)

        try:
            sequence = self.__map_pick_ban_sequence[0]
        except IndexError:
            raise SyntaxError

        next_pick_info = sequence.split("~")
        mode = next_pick_info[0]
        team = next_pick_info[1]

        if status is CaptainStatus.NOT_CAPTAIN or (team == "A" and status is not CaptainStatus.CAPTAIN_A) or \
                (team == "B" and status is not CaptainStatus.CAPTAIN_B):
            raise SyntaxError

        if is_ban and mode == "P" or not is_ban and mode == "X":
            raise SyntaxError

        if self.__wait_for_side_pick and ((mode == "P" and team == "B") or (mode == "X" and team == "A")):
            raise SyntaxError

        if map not in self.__unselected_maps:
            raise SyntaxError

        self.__map_pick_ban_sequence.pop(0)
        self.__unselected_maps.remove(map)

        decider = None

        if len(self.__map_pick_ban_sequence) == 0:
            index = random.randint(0, len(self.__unselected_maps) - 1)
            decider = self.__unselected_maps.pop(index)
            self.__picked_maps.append(decider)

        return status, decider
