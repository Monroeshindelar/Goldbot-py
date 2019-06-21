def read_config(file_path):
    config_dictionary = {}
    with open(file_path, "r") as config_file:
        for line in config_file:
            line = line.strip()
            (key, val) = line.split('=')
            config_dictionary[key] = val
    return config_dictionary
