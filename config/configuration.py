class Configuration:

    def __init__(self, configuration: dict) -> None:
        self.__config: dict = configuration

    def show_diagram(self)->bool:
        return 'show_diagram' in self.__config and self.__config['show_diagram'] == True

    def get_root_nodes(self) -> dict:
        return self.__config['nodes']['root']

    def get_common_nodes(self) -> dict:
        return self.__config['nodes']['common']
