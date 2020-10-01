import os
import yaml
from pathlib import Path


class Config:
    __instance = None

    @staticmethod
    def get_config_property(*props):
        if Config.__instance is None:
            Config()

        return Config.__get_config_property_helper(Config.__instance.CONF, list(props))

    @staticmethod
    def __get_config_property_helper(conf, props):
        if len(props) == 0:
            return conf
        elif props[0] not in conf.keys():
            return None

        return Config.__get_config_property_helper(conf[props[0]], props[1:])

    def __init__(self):
        if Config.__instance is not None:
            raise Exception("Error: Cannot create another instance of Config, one already exists.")
        else:
            Config.__instance = self
            with open(Path(os.getcwd()) / "bin/config.yml") as f:
                self.CONF = yaml.load(f, Loader=yaml.FullLoader)
