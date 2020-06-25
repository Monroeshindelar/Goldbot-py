from core.model.wedlocke.PairStatus import PairStatus


class Pair:
    def __init__(self, initial_encounter, route):
        self.__encounters = (initial_encounter, None)
        self.__route = route
        self.__status = PairStatus.INCOMPLETE
        self.__notes = None

    def get_route(self):
        return self.__route

    def get_notes(self):
        return self.__notes

    def set_notes(self, notes):
        self.__notes = notes

    def get_status(self):
        return self.__status

    def get_encounters(self):
        return self.__encounters

    def team(self):
        self.__status = PairStatus.TEAM

    def box(self):
        self.__status = PairStatus.BOXED

    def kill(self):
        self.__status = PairStatus.DEAD

    def set_second_encounter(self, encounter):
        if encounter.get_owner() != self.__encounters[0].get_owner():
            self.__encounters = (self.__encounters[0], encounter)
            self.__status = PairStatus.UNASSIGNED
