import json
from typing import List

from models.data.channel import Channel


class Configuration:
    __config: dict = None

    # ----------------------------------------------------------------------------------------------------------------------#
    @staticmethod
    def _config() -> dict:
        if Configuration.__config is None:
            configuration_file = open('config/configuration.json', 'r')
            Configuration.__config = json.load(configuration_file)
            configuration_file.close()
        return Configuration.__config

    @staticmethod
    def get_root_nodes() -> dict:
        return Configuration._config()['nodes']['root']

    @staticmethod
    def get_common_nodes() -> dict:
        return Configuration._config()['nodes']['common']
