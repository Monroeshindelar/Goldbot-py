import os
import pickle
import requests
import logging

LOGGER = logging.getLogger("goldlog")


def read_config(file_path, delim="="):
    config_dictionary = {}
    with open(file_path, "r") as config_file:
        for line in config_file:
            line = line.strip()
            (key, val) = line.split(delim)
            config_dictionary[key] = val
    return config_dictionary


def read_or_create_file_pkl(file_path):
    contents = None
    if os.path.exists(file_path):
        with open(file_path, "rb") as file:
            contents = pickle.load(file)
            file.close()
    else:
        file = open(file_path, "wb+")
        contents = []
        pickle.dump(object, file, pickle.HIGHEST_PROTOCOL)
        file.close()
    return contents


def save_to_file_pkl(content, file_path):
    with open(file_path, 'wb+') as file:
        pickle.dump(content, file, pickle.HIGHEST_PROTOCOL)


def fix_corrupt_file(file_path):
    os.remove(file_path)
    read_or_create_file_pkl(file_path)


def download_image_from_web(url, file_name):
    if os.path.isfile(file_name):
        with open(file_name, 'wb') as handle:
            response = requests.get(url, stream=True)

            if not response.ok:
                LOGGER.warn(response)

            for block in response.iter_content(1024):
                if not block:
                    break

                handle.write(block)
