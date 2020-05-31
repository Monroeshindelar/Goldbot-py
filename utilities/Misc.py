import os
import pickle
import logging
import json

LOGGER = logging.getLogger("goldlog")


def read_save_file(file_path):
    if os.path.exists(file_path):
        LOGGER.info("Misc::read_save_file - Reading data from " + file_path + " into memory")
        with open(file_path, "rb") as file:
            contents = pickle.load(file)
            file.close()
    else:
        LOGGER.info("Misc::read_save_file - No save data exists at " + file_path + ". Starting with fresh data.")
        contents = []
    return contents


def save_file(content, file_path):
    with open(file_path, 'wb+') as file:
        LOGGER.info("Misc::save_file - Saving data to disk at " + file_path)
        pickle.dump(content, file, pickle.HIGHEST_PROTOCOL)


def read_json_safe(path):
    if not os.path.isfile(path) or os.path.isfile(path) and not os.access(path, os.R_OK):
        with open(path, "w") as f:
            json.dump({}, f, indent=4)

    with open(path) as f:
        j = json.load(f)

    return j
