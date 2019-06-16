def read_config(file_path):
    d = {}
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            (key, val) = line.split('=')
            d[key] = val
    return d
