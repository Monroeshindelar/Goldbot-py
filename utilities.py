def read_token(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()
        return lines[0].strip()
