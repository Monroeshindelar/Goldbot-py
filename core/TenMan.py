from _global.Config import Config
from core.model.TenMan.Team import Team
from core.model.TenMan.Game import Game
from core.model.TenMan.TeamStatus import TeamStatus
from core.model.TenMan.Side import Side
from typing import Tuple, List
from core.model.TenMan.TeamsManager import TeamsManager
from core.model.TenMan.MapPickBanEntry import MapPickBanEntry
from core.model.TenMan.PickBanMode import PickBanMode
from ErrorHandling.Exceptions.TenMan.TurnError import TurnError
from ErrorHandling.Exceptions.TenMan.PhaseError import PhaseError
from ErrorHandling.Exceptions.TenMan.EntityError import EntityError
from ErrorHandling.Exceptions.TenMan.InitializationError import InitializationError
from random import randint


class TenMan:
    def __init__(self, participant_id_list: list, game: Game):
        # Initial list of participants
        self.__unselected_participants = participant_id_list
        # Game being played
        self.__game = game
        # Amount of games to be played
        self.__game_type = "bo3"

        # Get the list of maps for the game being played.
        if self.__game == Game.CSGO:
            self.__unselected_maps = [m.lower() for m in Config.get_config_property("tenman", "maps", "csgo")]
            self.__map_pick_ban_sequence = [MapPickBanEntry(s) for s in Config.get_config_property("tenman", "mapPickBanSequence",
                                      "csgo", self.__game_type).split("-")]
        elif self.__game == Game.VALORANT:
            self.__unselected_maps = [m.lower() for m in Config.get_config_property("tenman", "maps", "valorant")]
            self.__map_pick_ban_sequence = [MapPickBanEntry(s) for s in Config.get_config_property("tenman", "mapPickBanSequence", "valorant",
                                      self.__game_type).split("-")]

        self.__teams_manager = None

        # List of maps to pay
        self.__picked_maps = []
        # Order captains pick players
        self.__player_pick_sequence = [TeamStatus.get(s) for s in Config.get_config_property("tenman", "playerPickSequence").split("-")]
        # Flag set when waiting for other team to pick side
        self.__wait_for_side_pick = False
        # Team that picks the side
        self.__side_pick_team = None

        # Bail if there are not exactly 10 members
        # if len(self.__player_pick_sequence) < 10 or len(self.__player_pick_sequence) > 10:
        #     raise SyntaxError
        #
        # # Bail if the number of players on each team would not be equal
        # if self.__player_pick_sequence.count(TeamStatus.A) != self.__player_pick_sequence.count(TeamStatus.B):
        #     raise SyntaxError

    def get_remaining_participant_ids(self) -> List[int]:
        """
        :return: List of participants that have not been placed on a team
        """
        return self.__unselected_participants

    def get_remaining_maps(self) -> List[str]:
        """
        :return: List of maps that have not been selected
        """
        return [m.capitalize() for m in self.__unselected_maps]

    def get_captain_team_status(self, captain_id: int):
        if self.__teams_manager is None:
            raise InitializationError("There are no captains yet. Could not get captain team status")

        return self.__teams_manager.get_team_status_from_captain(captain_id)

    def get_side_pick_team(self) -> TeamStatus:
        return self.__side_pick_team

    def get_teams(self) -> Tuple[Team, Team]:
        if self.__teams_manager is None:
            raise InitializationError("No teams available. Captains have not been selected yet.")

        return self.__teams_manager.get_teams()

    def peek_next_player_pick(self) -> TeamStatus:
        return self.__player_pick_sequence[0]

    def peek_next_map_pick_ban(self) -> MapPickBanEntry:
        return self.__map_pick_ban_sequence[0]

    def set_or_pick_captains(self, captain_ids: List[int]) -> Tuple[int, int]:
        """
        Sets the captains if they are selected manually. If no captain ids are provided to the function they will be
        randomly selected and set
        :param captain_ids: A list that should either contain 0 ore two captain ids
        :return: A tuple that contains the ids of the two captains for each team. Index 0 is captain A and
                 index 1 is captain B
        """
        # Bail if there are already people on the team
        # if len(self.__team_a) > 0 or len(self.__team_b) > 0:
        #     raise SyntaxError
        if self.__teams_manager is not None:
            raise InitializationError("A ten man has already been initialized. Captains have been set.")

        # Set the captains if they are provided. Randomly select them if they are not
        try:
            self.__unselected_participants.remove(captain_ids[0])
            self.__unselected_participants.remove(captain_ids[1])
        except (TypeError, IndexError):
            captain_ids = []
            for x in range(2):
                index = randint(0, len(self.__unselected_participants) - 1)
                captain_ids.append(self.__unselected_participants.pop(index))

        # # Add the captains to the team
        self.__teams_manager = TeamsManager(captain_ids[0], captain_ids[1])
        return captain_ids[0], captain_ids[1]

    def pick_player(self, player_id: int, captain_id: int) -> Tuple[int, TeamStatus]:
        """
        :param player_id: Id of player being picked
        :param captain_id: Id of captain picking the player
        :return: A tuple that contains the id and team of the last pick if one exits. None/None otherwise
        """
        # Bail if the caller wasn't the captain
        if not self.__captain_turn(captain_id):
            raise TurnError("Incorrect captain attempting to pick player.")

        # Bail if there are no more participants to select
        if len(self.__unselected_participants) == 0:
            raise PhaseError("It is no longer the player pick phase")

        # Remove the participant from the list. Bail if they selected someone who isn't a participant
        try:
            self.__unselected_participants.remove(player_id)
        except ValueError:
            raise EntityError("Selected player is not an eligible unselected participant.")

        # Let the teams manager add the player to the correct team
        self.__teams_manager.add_player(player_id, self.__teams_manager.get_team_status_from_captain(captain_id))
        self.__player_pick_sequence.pop(0)

        last_pick_id = None
        last_pick_captain_status = None

        # If there is only one more player, automatically add them to the team
        if len(self.__unselected_participants) == 1:
            last_pick_id = self.__unselected_participants.pop(0)
            last_pick_captain_status = self.__player_pick_sequence.pop(0)
            self.__teams_manager.add_player(last_pick_id, last_pick_captain_status)

        return last_pick_id,  last_pick_captain_status

    def ban_map(self, game_map: str, captain_id: int) -> str:
        """
        :param game_map: Map being banned
        :param captain_id: Id of captain banning map
        :return: A tuple containing the team of the captain that banned the map and the name of the map
        """
        self.__map_pick_ban_helper(game_map, captain_id, True)
        decider = None
        if len(self.__map_pick_ban_sequence) == 0:
            decider = self.__get_decider_map()

        return decider

    def pick_map(self, game_map: str, captain_id: int):
        """
        :param game_map: Map being picked
        :param captain_id: Id of captain banning map
        :return: The team of the calling captain
        """
        self.__map_pick_ban_helper(game_map, captain_id, False)
        self.__picked_maps.append(game_map)
        self.__wait_for_side_pick = True

    def pick_side(self, captain_id: int, side: str) -> Tuple[Side, str]:
        """
        :param captain_id: Id of calling captain
        :param side: picked side
        :return: A tuple containing the picked side, the team of the captain who picked, and the decider map pick if
                 one exists (otherwise none)
        """
        if not len(self.__unselected_participants) == 0:
            raise PhaseError("Player pick phase is not over.")

        if not self.__wait_for_side_pick:
            raise PhaseError("It is not time to pick a starting side.")

        status = self.__teams_manager.get_team_status_from_captain(captain_id)

        # Bail if the wrong team is trying to pick side
        if self.__side_pick_team is TeamStatus.A and not status == TeamStatus.A or \
                self.__side_pick_team is TeamStatus.B and not status == TeamStatus.B:
            raise TurnError("Incorrect captain attempting to issue side pick.")

        # Set wait for side pick flag to reflect a side has been picked
        self.__wait_for_side_pick = False
        # Reset side pick team
        self.__side_pick_team = None

        # Check to see if a decider map needs to be picked
        # This only really happens for the valorant game pick currently, because there is an even number of maps and
        # there are too little maps for both teams to ban a map and play a best of three.
        # If there are multiple remaining maps, one will be randomly selected.
        decider = None
        if len(self.__map_pick_ban_sequence) == 0:
            decider = self.__get_decider_map()

        return Side.get(side), decider

    def __captain_turn(self, captain_id: int) -> bool:
        if self.__teams_manager is None:
            raise InitializationError("Cannot check captain turn. Teams have not been created.")

        return self.__player_pick_sequence[0] == self.__teams_manager.get_team_status_from_captain(captain_id)

    def __map_pick_ban_helper(self, game_map: str, captain_id: int, is_ban: bool):
        if len(self.__unselected_participants) > 0:
            raise PhaseError("Player pick phase has not been completed.")

        try:
            sequence = self.__map_pick_ban_sequence[0]
        except IndexError:
            raise PhaseError("Map pick/ban phase is over.")

        status = self.__teams_manager.get_team_status_from_captain(captain_id)
        self.__set_side_pick_team(status)

        mode = sequence.get_mode()
        team = sequence.get_team_status()

        if status != team:
            raise TurnError("Incorrect captain attempting to issue map selection.")

        if (is_ban and mode == PickBanMode.PICK) or (not is_ban and mode == PickBanMode.BAN):
            raise PhaseError("Incorrect pick/ban mode.")

        if self.__wait_for_side_pick:
            raise PhaseError("Waiting for side pick. Cannot issue map pick/bans.")

        if game_map not in self.__unselected_maps:
            raise EntityError("Requested map is not an available unselected map.")

        self.__map_pick_ban_sequence.pop(0)
        self.__unselected_maps.remove(game_map)

    def __set_side_pick_team(self, map_pick_team: TeamStatus):
        if map_pick_team is not TeamStatus.A and map_pick_team is not TeamStatus.B:
            raise SyntaxError
        elif map_pick_team is TeamStatus.A:
            self.__side_pick_team = TeamStatus.B
        elif map_pick_team is TeamStatus.B:
            self.__side_pick_team = TeamStatus.A

    def __get_decider_map(self) -> str:
        if len(self.__map_pick_ban_sequence) != 0:
            raise PhaseError("Tried to select decider map before the pick/ban sequence was over.")

        index = randint(0, len(self.__unselected_maps) - 1)
        return self.__unselected_maps.pop(index)
