import yaml
from utilities.misc import get_project_dir
from typing import List


class Config:
    __instance = None

    @staticmethod
    def get_config_property(*props):
        if Config.__instance is None:
            Config()

        return Config.__get_config_property_helper(Config.__instance.CONF, list(props))

    @staticmethod
    def update_config_property_and_write(key: str, value: object):
        if Config.__instance is None:
            Config()

        Config.__instance.CONF = Config.__update_config_property_and_write_helper(key.split("/"), value,
                                                                                  Config.__instance.CONF)
        with open(str(get_project_dir() / "bin/config.yml"), "w+") as f:
            yaml.dump(Config.__instance.CONF, f)

    @staticmethod
    def __get_config_property_helper(conf, props):
        if len(props) == 0:
            return conf
        elif props[0] not in conf.keys():
            return None

        return Config.__get_config_property_helper(conf[props[0]], props[1:])

    @staticmethod
    def __update_config_property_and_write_helper(keys: List[str], value: object, config: dict) -> dict:
        if len(keys) == 0:
            return config
        key = keys.pop(0)
        if len(keys) == 0:
            config[key] = value
        else:
            config[key] = Config.__update_config_property_and_write_helper(keys, value, config[key])

        return config

    def __init__(self):
        if Config.__instance is not None:
            raise Exception("Error: Cannot create another instance of Config, one already exists.")
        else:
            Config.__instance = self
            with open(str(get_project_dir() / "bin/config.yml")) as f:
                self.CONF = yaml.load(f, Loader=yaml.FullLoader)
