import os
import pickle
import logging
import json
import re
from logging.handlers import TimedRotatingFileHandler

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


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("goldlog")
    logger.setLevel(logging.DEBUG)

    fh = TimedRotatingFileHandler("bin/log/gold.log", when="midnight", interval=1)
    fh.setLevel(logging.DEBUG)
    fh.suffix = "%Y%m%d"
    fh.extMatch = re.compile(r"^\d{8}$")

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


