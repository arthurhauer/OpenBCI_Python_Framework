import json


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

    # ----------------------------------------------------------------------------------------------------------------------#

    # region General Settings
    @staticmethod
    def get_general_settings() -> dict:
        return Configuration._config()['general']

    @staticmethod
    def get_maximum_parallel_jobs() -> int:
        return Configuration.get_general_settings()['maximum-parallel-jobs']

    @staticmethod
    def get_sampling_frequency() -> int:
        return Configuration.get_general_settings()['sampling-frequency']

    # end_region General Settings

    # ----------------------------------------------------------------------------------------------------------------------#

    # region Open-BCI Settings

    @staticmethod
    def get_open_bci_settings() -> dict:
        return Configuration._config()['open_bci']

    @staticmethod
    def get_open_bci_log_level() -> str:
        return Configuration.get_open_bci_settings()['log_level']

    @staticmethod
    def get_open_bci_board() -> str:
        return Configuration.get_open_bci_settings()['board']

    @staticmethod
    def get_open_bci_communication() -> dict:
        return Configuration.get_open_bci_settings()['communication']

    @staticmethod
    def get_open_bci_communication_serial_port() -> str:
        return Configuration.get_open_bci_communication()['serial_port']

        # end_region Open-BCI Settings
    # ----------------------------------------------------------------------------------------------------------------------#
