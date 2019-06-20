from utilities import read_config


class Config:
    __instance = None

    @staticmethod
    def get_config_property(config_property):
        if Config.__instance is None:
            Config()
        return Config.__instance.CONF[config_property]

    def __init__(self):
        if Config.__instance is not None:
            raise Exception("Error: Cannot create another instance of Config, one already exists.")
        else:
            Config.__instance = self
            self.CONF = read_config("bin/config.txt")
