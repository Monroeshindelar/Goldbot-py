import os
import pickle
import logging
import json

LOGGER = logging.getLogger("goldlog")


def read_save_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as file:
            contents = pickle.load(file)
            file.close()
    else:
        contents = []
    return contents


def save_file(content, file_path):
    with open(file_path, 'wb+') as file:
        pickle.dump(content, file, pickle.HIGHEST_PROTOCOL)


def read_json_safe(path):
    if not os.path.isfile(path) or os.path.isfile(path) and not os.access(path, os.R_OK):
        with open(path, "w") as f:
            json.dump({}, f, indent=4)

    with open(path) as f:
        j = json.load(f)

    return j


def create_save_dir(path):
    try:
        os.makedirs(path)
    except FileExistsError:
        pass
