import os
import pickle
import logging

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
