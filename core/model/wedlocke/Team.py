from core.model.wedlocke.PairStatus import PairStatus


class Team:
    def __init__(self):
        self.__pairs = []

    def at_capacity(self):
        return len(self.__pairs) == 6

    def add_to_team(self, pair):
        if self.at_capacity():
            raise SyntaxError
        if pair.get_status() == PairStatus.INCOMPLETE:
            raise SyntaxError
        if pair in self.__pairs:
            raise SyntaxError

        pair.team()
        self.__pairs.append(pair)

    def remove_from_team(self, pair):
        self.__pairs.remove(pair)