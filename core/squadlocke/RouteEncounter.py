import pandas
import logging
import string
from tabulate import tabulate
from numpy.random import choice

from core.squadlocke.Encounter import Encounter
from core.squadlocke.SquadlockeConstants import ROUTE_CACHE, COLUMNS, WEATHER_DICT, ENCOUNTER_AREA_DICT

LOGGER = logging.getLogger("goldlog")
PRETTY_TABLE_HEADERS = ["Name(Sword)", "Name(Shield)", "Encounter Rate", "Encounter Area"]
WHITELIST = {'and', 'the', 'is', 'in'}


class RouteEncounter:
    def __init__(self, route):
        file_name = ROUTE_CACHE + route.replace(' ', '').translate(str.maketrans('', '', string.punctuation)) + '.csv'
        self.__df = pandas.read_csv(file_name)
        self.__included_values = {
            COLUMNS[3]: list(self.__df[COLUMNS[3]].unique()),
            COLUMNS[4]: list(self.__df[COLUMNS[4]].unique()),
            COLUMNS[5]: list(self.__df[COLUMNS[5]].unique())
        }

    def get_encounter(self):
        filtered_table = self.__apply_filters()
        if filtered_table.empty:
            return None
        total = sum(filtered_table[COLUMNS[2]])

        normalized_rates = [rate / total for rate in filtered_table[COLUMNS[2]]]
        index = choice(filtered_table['idx'], p=normalized_rates)

        return Encounter(name_v1=filtered_table.loc[index, COLUMNS[0]], name_v2=filtered_table.loc[index, COLUMNS[1]],
                         rate=filtered_table.loc[index, COLUMNS[2]], n_rate=round((filtered_table.loc[index, COLUMNS[2]]
                                                                                   / total) * 100, 2),
                         area=filtered_table.loc[index, COLUMNS[3]], section=filtered_table.loc[index, COLUMNS[4]],
                         weather=WEATHER_DICT.inverse[filtered_table.loc[index, COLUMNS[5]]][0],
                         sprite_v1=filtered_table.loc[index, COLUMNS[6]], sprite_v2=filtered_table.loc[index,
                                                                                                       COLUMNS[7]])

    def get_info(self):
        tables = {}
        sections = self.__df['section'].unique()
        for section in sections:
            section_table = self.__df[self.__df[COLUMNS[4]] == section]
            weathers = section_table['weather'].unique()
            rows = {}
            for weather in weathers:
                weather_table = section_table[section_table[COLUMNS[5]] == weather]
                w = []
                for idx, row in weather_table.iterrows():
                    if pandas.isna(row[COLUMNS[1]]):
                        vx_name = ''
                    else:
                        vx_name = row[COLUMNS[1]]
                    w.append([row[COLUMNS[0]], vx_name, str(row[COLUMNS[2]]) + "%",ENCOUNTER_AREA_DICT
                             .inverse[row[COLUMNS[3]]][0]])
                rows.update({WEATHER_DICT.inverse[weather][0]: tabulate(w, PRETTY_TABLE_HEADERS)})
            tables.update({section: rows})
        return tables

    def add_area_filter(self, areas, mode):
        self.__add_filters(self.__get_filter_value_ids(areas, ENCOUNTER_AREA_DICT), mode, COLUMNS[3])

    def add_section_filter(self, sections, mode):
        section_ids = []
        unique_sections = list(self.__df[COLUMNS[4]].unique())
        for section in sections:
            if not section.isdigit():
                tokens = section.split(" ")
                normalized = " ".join([token.title() if token not in WHITELIST else token for token in tokens])
                if normalized in unique_sections:
                    section_ids.append(normalized)
            else:
                section = int(section)
                if len(unique_sections) > section > 0:
                    section_ids.append(unique_sections[section])
        self.__add_filters(section_ids, mode, COLUMNS[4])

    def add_weather_filter(self, weathers, mode):
        self.__add_filters(self.__get_filter_value_ids(weathers, WEATHER_DICT), mode, COLUMNS[5])

    def __add_filters(self, values, mode, key):
        if mode == -1:
            for value in values:
                if value in self.__included_values[key]:
                    self.__included_values[key].remove(value)
        elif mode == 0:
            self.__included_values[key] = list(values)
        elif mode == 1:
            self.__included_values[key].append(list(values))

    def __apply_filters(self):
        df = self.__df
        for key in self.__included_values:
            df = df[df[key].isin(self.__included_values[key])]
        return df

    @staticmethod
    def __get_filter_value_ids(values, bidict):
        value_ids = []
        for value in values:
            value = str(value)
            if not value.isdigit():
                tokens = value.split(' ')
                normalized = " ".join([token.title() if token not in WHITELIST else token for token in tokens])
                if normalized in bidict.keys():
                    value_ids.append(bidict[normalized])
            else:
                value = int(value)
                if value in bidict.inverse.keys():
                    value_ids.append(value)
        return value_ids
