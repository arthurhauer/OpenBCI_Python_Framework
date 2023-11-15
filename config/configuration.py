class Configuration:

    def __init__(self, configuration: dict) -> None:
        self.__config: dict = configuration

    def get_root_nodes(self) -> dict:
        return self.__config['nodes']['root']

    def get_common_nodes(self) -> dict:
        return self.__config['nodes']['common']
