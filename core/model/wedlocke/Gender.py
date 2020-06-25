from enum import Enum


class Gender(Enum):
    FEMALE = 0
    MALE = 1
    UNDEFINED = 2

    @staticmethod
    def get(g):
        if g.lower() == "female" or g.lower() == "f":
            return Gender.FEMALE
        elif g.lower() == "male" or g.lower() == "m":
            return Gender.MALE
        elif g.lower() == "undefined" or g.lower() == "u":
            return Gender.UNDEFINED
        else:
            raise ValueError
