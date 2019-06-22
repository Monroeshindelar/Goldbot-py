import os
import pickle


def read_config(file_path):
    config_dictionary = {}
    with open(file_path, "r") as config_file:
        for line in config_file:
            line = line.strip()
            (key, val) = line.split('=')
            config_dictionary[key] = val
    return config_dictionary


def read_or_create_file_pkl(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as file:
            _object = pickle.load(file)
    else:
        file = open(file_path, "wb+")
        _object = []
        pickle.dump(object, file, pickle.HIGHEST_PROTOCOL)
    return _object
