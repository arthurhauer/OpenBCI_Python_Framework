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
    def set_sampling_frequency(sampling_frequency: int):
        Configuration.get_general_settings()['sampling-frequency'] = sampling_frequency

    @staticmethod
    def get_sampling_frequency() -> int:
        return Configuration.get_general_settings()['sampling-frequency']

    @staticmethod
    def get_graphing_settings() -> dict:
        return Configuration.get_general_settings()['graph']

    @staticmethod
    def get_graphing_window_size() -> int:
        return Configuration.get_graphing_settings()['window-size']

    # end_region General Settings

    # ----------------------------------------------------------------------------------------------------------------------#

    # region Open-BCI Settings

    @staticmethod
    def get_open_bci_settings() -> dict:
        return Configuration._config()['open_bci']

    @staticmethod
    def get_open_bci_log_level() -> str:
        return Configuration.get_open_bci_settings()['log-level']

    @staticmethod
    def get_open_bci_board() -> str:
        return Configuration.get_open_bci_settings()['board']

    @staticmethod
    def get_open_bci_communication() -> dict:
        return Configuration.get_open_bci_settings()['communication']

    @staticmethod
    def get_open_bci_communication_serial_port() -> str:
        return Configuration.get_open_bci_communication()['serial-port']

    @staticmethod
    def get_open_bci_data_callback_frequency_ms() -> int:
        return Configuration.get_open_bci_settings()['data-callback-frequency-ms']
        # end_region Open-BCI Settings

    # ----------------------------------------------------------------------------------------------------------------------#

    # region Pre-Processing Settings

    @staticmethod
    def get_preprocessing_settings() -> list:
        return Configuration._config()['preprocessing']

    @staticmethod
    def get_proprocessing_setting_at_index(index: int) -> dict:
        return Configuration.get_preprocessing_settings()[index]

        # end_region Pre-Processing Settings
    # ----------------------------------------------------------------------------------------------------------------------#
