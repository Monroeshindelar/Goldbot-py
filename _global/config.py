import os
import sys
from pathlib import Path

import yaml


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
            project_dir = Path(os.path.abspath(sys.modules["__main__"].__file__)) / ".."
            with open(project_dir / "bin/config.yml") as f:
                self.CONF = yaml.load(f, Loader=yaml.FullLoader)
