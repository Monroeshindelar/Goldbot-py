from core.model.wedlocke.Encounter import Encounter
from core.model.wedlocke.Pair import Pair
from core.model.wedlocke.Team import Team
from core.model.wedlocke.PairStatus import PairStatus


class Wedlocke:
    def __init__(self, participant1, participant2, game):
        self.__participants = (participant1, participant2)
        self.__game = game
        self.__pairs = {}
        self.__team = Team()

    def get_game(self):
        return self.__game

    def get_team(self):
        return self.__team

    def get_pairs(self):
        return self.__pairs

    def get_participants(self):
        return self.__participants

    def create_or_append_pair(self, species, gender, nickname, owner, route):
        encounter = Encounter(species, gender, nickname, owner)

        try:
            pair = self.__pairs[route]
            pair.set_second_encounter(encounter)
            try:
                self.__team.add_to_team(pair)
            except SyntaxError:
                pair.box()
        except KeyError:
            pair = Pair(encounter, route)
            self.__pairs[route] = pair

    def kill_pair(self, route):
        try:
            pair = self.__pairs[route]
            if pair.get_status() == PairStatus.TEAM:
                self.__team.remove_from_team(pair)
            pair.kill()
        except KeyError:
            pass
