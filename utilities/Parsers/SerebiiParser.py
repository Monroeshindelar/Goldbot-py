import requests
import pandas
import os
import logging
import string
from _global.SquadlockeConstants import COLUMNS, SECTION_REGEX, ENCOUNTER_TABLE_REGEX, GAME_REGEX, \
    ENCOUNTER_AREA_REGEX, WEATHER_DICT, ENCOUNTER_AREA_DICT, ROUTE_CACHE, SEREBII_NAME_REPLACEMENT_DICT
from bs4 import BeautifulSoup

LOGGER = logging.getLogger('goldlog')
BASE_URL = 'https://www.serebii.net/pokearth/galar/'


class SerebiiParser:

    @staticmethod
    def fetch_all_data():
        LOGGER.info("Fetching data for all routes")
        r = requests.get(BASE_URL)
        soup = BeautifulSoup(r.text, 'html.parser')
        form = soup.find('form', {'name': 'kalos'})
        select = form.find('select', {'name': 'SelectURL'})
        options = select.findAll('option')
        for option in options:
            SerebiiParser.parse_route(option.get_text().lower())
        LOGGER.info("Finished fetching route encounter data")

    @staticmethod
    def parse_route(route):
        df = pandas.DataFrame()
        # Pull the raw html from the website with the encounter information
        file_name = ROUTE_CACHE + route.replace(' ', '').translate(str.maketrans('', '', string.punctuation)) + '.csv'
        if os.path.isfile(file_name):
            LOGGER.info("Skipping fetch for " + route + " because encounter data already exists.")
            return
        url = BASE_URL + route.replace(' ', '') + '.shtml'
        LOGGER.info("Fetching data for " + route + " from " + url)
        r = requests.get(url)
        # Run html through a parser, fix some bullshit from serebii where extra tags cause the parser to fail
        soup = BeautifulSoup(r.text.replace('</h3></h3>', '</h3>').replace('</h4></h4>', '</h4>'), 'html.parser')

        # Some pages have sections, but the tables in the html aren't tied to those sections in any way
        # If there are encounters, we have to just keep a list of the tables that appear in between the
        # section elements
        areas = soup.findAll('a', {'name': SECTION_REGEX})
        area_map = {}
        if areas is not None and len(areas) > 0:
            for area in areas:
                area_name = area.next_element.get_text()
                table_list = []
                for tag in area.next_elements:
                    if tag in areas:
                        break
                    if tag.name == 'table':
                        table_class = tag.get('class')
                        if table_class is not None and len(table_class) > 0 and ENCOUNTER_TABLE_REGEX\
                                .match(table_class[0]):
                            table_list.append(tag)
                if len(table_list) > 0:
                    area_map.update({area_name: table_list})
        else:
            t = soup.findAll('table', ENCOUNTER_TABLE_REGEX)
            if len(t) > 0:
                area_map.update({'Main Area': t})

        # every section has its own set of tables associated with it
        for section in area_map.keys():
            tables = area_map.get(section)
            sw_tables = []
            sh_tables = []
            # split up all tables by game version
            for table in tables:
                td = table.find('td', {'class': GAME_REGEX})
                if td is None:
                    continue
                elif td['class'][0] == 'lgeevee':
                    sh_tables.append(table)
                elif td['class'][0] == 'lgpika':
                    sw_tables.append(table)

            for table_sw, table_sh in zip(sw_tables, sh_tables):
                encounter_area = table_sw.find("td", {"class": ENCOUNTER_AREA_REGEX}).get_text()
                weather = table_sw.find('td', {'class': 'black'})
                if weather is not None:
                    weather = WEATHER_DICT[weather.get_text()]
                else:
                    weather = -1

                current_names_sw = [name.get_text() for name in table_sw.findAll("td", {"class": "name"})]
                current_names_sh = [name.get_text() for name in table_sh.findAll("td", {"class": "name"})]
                try:
                    current_rates_sw = [int(rate.get_text().replace('%', '')) for rate in
                                        table_sw.findAll("td", {"class": "rate"})]
                except ValueError:
                    continue
                current_rates_sh = [int(rate.get_text().replace('%', '')) for rate in
                                    table_sh.findAll("td", {"class": "rate"})]
                current_sprites_sw = [sprite['src'] for sprite in table_sw.findAll("img", {"class": "wildsprite"})]
                current_sprites_sh = [sprite['src'] for sprite in table_sh.findAll("img", {"class": "wildsprite"})]
                SerebiiParser.normalize(current_names_sw, current_names_sh, current_rates_sw, current_rates_sh,
                                        current_sprites_sw, current_sprites_sh, ENCOUNTER_AREA_DICT[encounter_area],
                                        section, weather)
                if encounter_area in SEREBII_NAME_REPLACEMENT_DICT.keys():
                    encounter_area = SEREBII_NAME_REPLACEMENT_DICT[encounter_area]
                df = df.append(SerebiiParser.normalize(current_names_sw, current_names_sh, current_rates_sw,
                                                       current_rates_sh, current_sprites_sw, current_sprites_sh,
                                                       ENCOUNTER_AREA_DICT[encounter_area], section,
                                                       weather), ignore_index=True)

        if not df.empty:
            LOGGER.info("Saving fetched data to disk at " + file_name)
            df.index.name = 'idx'
            df.to_csv(file_name)

    @staticmethod
    def normalize(names_sw, names_sh, rates_sw, rates_sh, sprites_sw, sprites_sh, area, section, weather):
        rows = []
        if len(names_sw) == len(names_sh):
            for name_sw, name_sh, rate, sprite_sw, sprite_sh in zip(names_sw, names_sh, rates_sw, sprites_sw,
                                                                    sprites_sh):
                current = {COLUMNS[0]: name_sw, COLUMNS[1]: '', COLUMNS[2]: rate, COLUMNS[3]: area, COLUMNS[4]: section,
                           COLUMNS[5]: weather, COLUMNS[6]: sprite_sw, COLUMNS[7]: ''}
                if name_sw != name_sh:
                    current.update({COLUMNS[1]: name_sh, COLUMNS[7]: sprite_sh})
                rows.append(current)
            return pandas.DataFrame(rows)

        if sum(rates_sw) != 100 or sum(rates_sh) != 100:
            [rows.append({COLUMNS[0]: name, COLUMNS[1]: '', COLUMNS[2]: rate, COLUMNS[3]: area, COLUMNS[4]: section,
             COLUMNS[5]: weather, COLUMNS[6]: sprite, COLUMNS[7]: ''}) for name, rate, sprite in
             zip(max([names_sw, names_sh], key=len), max([rates_sw, rates_sh], key=len), max([sprites_sw, sprites_sh],
                                                                                             key=len))]
            return pandas.DataFrame(rows)

        num_suspects = abs(len(names_sw) - len(names_sh))

        v1unique = [{'name': item[0], 'rate': item[1], 'sprite': item[2]} for item in
                    zip(names_sw, rates_sw, sprites_sw) if item[0] not in names_sh]
        v1common = [{'name': item[0], 'rate': item[1], 'sprite': item[2]} for item in
                    zip(names_sw, rates_sw, sprites_sw) if item[0] in names_sh]
        v2unique = [{'name': item[0], 'rate': item[1], 'sprite': item[2]} for item in
                    zip(names_sh, rates_sh, sprites_sh) if item[0] not in names_sw]
        v2common = [{'name': item[0], 'rate': item[1], 'sprite': item[2]} for item in
                    zip(names_sh, rates_sh, sprites_sh) if item[0] in names_sw]

        total_diff = sum([abs(item1['rate'] - item2['rate']) for item1, item2 in zip(v1common, v2common)])
        all_rates = set([item['rate'] for item in v1unique]) | set([item['rate'] for item in v2unique])

        for rate in all_rates:
            v1_with_rate = [item for item in v1unique if item['rate'] == rate]
            v2_with_rate = [item for item in v2unique if item['rate'] == rate]

            if len(v1_with_rate) != 0 and len(v2_with_rate) != 0 and len(v1_with_rate) != len(v2_with_rate):
                if len(v1_with_rate) > len(v2_with_rate):
                    v1_with_rate = v1_with_rate[abs(len(v1_with_rate) - len(v2_with_rate)):]
                else:
                    v2_with_rate = v2_with_rate[abs(len(v1_with_rate) - len(v2_with_rate)):]

            for v1, v2 in zip(v1_with_rate, v2_with_rate):
                v1common.append(v1)
                v2common.append(v2)
                v1unique.remove(v1)
                v2unique.remove(v2)

        if len(min([v1unique, v2unique], key=len)) == 0 and len(max([v1unique, v2unique], key=len)) == num_suspects and \
                sum([item['rate'] for item in max([v1unique, v2unique], key=len)]) == total_diff:
            merged_rate = 0
            i = 0
            for v1, v2 in zip(v1common, v2common):
                suspect = max([v1unique, v2unique], key=len)[i]
                current = {COLUMNS[0]: v1['name'], COLUMNS[1]: '', COLUMNS[2]: '', COLUMNS[3]: area, COLUMNS[4]: section,
                           COLUMNS[5]: weather, COLUMNS[6]: v1['sprite'], COLUMNS[7]: ''}

                if v1['name'] != v2['name']:
                    current.update({COLUMNS[1]: v2['name'], COLUMNS[7]: v2['sprite']})

                if v1['rate'] != v2['rate']:
                    diff = abs(v1['rate'] - v2['rate'])
                    current.update({COLUMNS[2]: min(v1['rate'], v2['rate'])})
                    extra = {COLUMNS[0]: '', COLUMNS[1]: '', COLUMNS[2]: diff, COLUMNS[3]: area, COLUMNS[4]: section,
                             COLUMNS[5]: weather, COLUMNS[6]: '', COLUMNS[7]: ''}
                    if len(names_sw) > len(names_sh):
                        extra.update({COLUMNS[0]: suspect['name'], COLUMNS[1]: v2['name'], COLUMNS[6]: suspect['sprite']
                                      , COLUMNS[7]: v2['sprite']})
                    else:
                        extra.update({COLUMNS[0]: v1['name'], COLUMNS[1]: suspect['name'], COLUMNS[6]: v1['sprite'],
                                      COLUMNS[7]: suspect['sprite']})
                    merged_rate += diff
                    if merged_rate == suspect['rate'] and i < num_suspects - 1:
                        merged_rate = 0
                        i = i + 1
                    rows.append(extra)
                else:
                    current.update({COLUMNS[2]: v1['rate']})
                rows.append(current)

        return pandas.DataFrame(rows)
