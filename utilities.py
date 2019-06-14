def read_token(filePath):
    with open(filePath, "r") as f:
        lines = f.readlines()
        return lines[0].strip()
