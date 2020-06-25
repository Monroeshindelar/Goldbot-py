class Encounter:
    def __init__(self, species, gender, nickname, owner):
        self.__species = species
        self.__gender = gender
        self.__nickname = nickname
        self.__owner = owner

    def get_species(self):
        return self.__species

    def get_gender(self):
        return self.__gender

    def get_nickname(self):
        return self.__nickname

    def get_owner(self):
        return self.__owner
