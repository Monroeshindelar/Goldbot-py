from pandas import isna


class Encounter:
    def __init__(self, name_v1, name_v2, rate, n_rate, area, section, weather, sprite_v1, sprite_v2):
        self.__name_v1 = name_v1
        self.__rate = rate
        self.__n_rate = n_rate
        self.__area = area
        self.__section = section
        self.__weather = weather
        self.__sprite_v1 = sprite_v1
        if isna(name_v2):
            self.__name_v2 = None
            self.__sprite_v2 = None
        else:
            self.__name_v2 = name_v2
            self.__sprite_v2 = sprite_v2

    def get(self):
        v1 = {'name': self.__name_v1, 'rate': self.__rate, 'n_rate': self.__n_rate, 'area': self.__area,
              'section': self.__section, 'weather': self.__weather, 'sprite': self.__sprite_v1}
        v2 = None
        if self.__name_v2 is not None:
            v2 = {'name': self.__name_v2, 'rate': self.__rate, 'n_rate': self.__n_rate, 'area': self.__area,
                  'section': self.__section, 'weather': self.__weather, 'sprite': self.__sprite_v2}
        return v1, v2
