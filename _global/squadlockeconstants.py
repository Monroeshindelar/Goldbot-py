import re
from utilities.bidict import bidict

# Horrible

ROUTE_CACHE = "bin/cache/squadlocke/route_encounters/"
COLUMNS = ["name_sw", "name_sh", "rate", "area", "section", "weather", "img_sw", "img_sh"]
SEREBII_NAME_REPLACEMENT_DICT = {"Random in Grass": "Shadow", "In the Water": "Surfing"}
ENCOUNTER_AREA_DICT = bidict({"Overworld": 0, "Shadow": 1, "Fishing": 2, "Shake a Berry Tree": 3,
                              "Coming from Underground": 4, "In the Sky": 5, "Surfing": 6,
                              "Interactable Pokémon": 7})
WEATHER_DICT = bidict({"None": -1, "Normal Weather": 0, "Overcast": 1, "Raining": 2, "Thunderstorm": 3, "Snowing": 4,
                       "Snowstorm": 5, "Intense Sun": 6, "Sandstorm": 7, "Fog": 8})
ENCOUNTER_TABLE_REGEX = re.compile("(extra)?dextable")
ENCOUNTER_AREA_REGEX = re.compile("(((double)?grass)|(berrytree)|(rocksmash)|(fish)|(sky)|(surf)|(interact))")
GAME_REGEX = re.compile("lg(pika|eevee)")
SECTION_REGEX = re.compile("xy.*")