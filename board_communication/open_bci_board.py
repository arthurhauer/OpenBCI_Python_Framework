from threading import Thread
from typing import List

import time
from brainflow import BrainFlowInputParams, BoardShim, BoardIds, LogLevels

from models.data.board_data import BoardData
from config.configuration import Configuration
from preprocessing.preprocessing import PreProcessing


class OpenBCIBoard:
    def __init__(self,preprocessing:PreProcessing,log_level:str="OFF",board:str="SYNTHETIC_BOARD") -> None:
        super().__init__()
        self._board = None
        self._timestamp_channel = None
        self._eeg_channels = None
        self._eeg_channel_names = None
        self._accelerometer_channels = None
        self._sampling_rate = None
        self._set_log_level()
        self._get_board()
        self.get_eeg_channels()
        self.get_accelerometer_channels()
        self._run_stream_loop: bool = False
        self._data_loop_thread: Thread = Thread(target=self._stream_data_loop, daemon=True)
        self._data_callback = None
        self._preprocessing = preprocessing


    @classmethod
    def from_config_json(cls):
        cls.__init__(
            preprocessing=PreProcessing.from_config_json(),
            log_level=Configuration.get_open_bci_log_level(),
            board=Configuration.get_open_bci_board()
        )

    def _set_log_level(self,log_level:str="OFF"):
        if log_level is None:
            log_level = "OFF"
        log_level = "LEVEL_" + log_level
        BoardShim.set_log_level(LogLevels[log_level])

    def _get_board_type(self,board:str="SYNTHETIC_BOARD") -> int:
        return BoardIds[board]

    def _get_brain_flow_input_parameters(self) -> BrainFlowInputParams:
        brain_flow_parameters = BrainFlowInputParams()
        # TODO Adicionar outras formas de comunicação
        # brain_flow_parameters.ip_port
        # brain_flow_parameters.serial_port
        # brain_flow_parameters.mac_address
        # brain_flow_parameters.other_info
        # brain_flow_parameters.serial_number
        # brain_flow_parameters.ip_address
        # brain_flow_parameters.ip_protocol
        # brain_flow_parameters.timeout
        # brain_flow_parameters.file
        if Configuration.get_open_bci_communication_serial_port() is not None:
            brain_flow_parameters.serial_port = Configuration.get_open_bci_communication_serial_port()
        else:
            raise Exception("configuration.openbci.communication.unsupported")
        return brain_flow_parameters

    def _get_board(self) -> BoardShim:
        if self._board is None:
            self._board = BoardShim(self._get_board_type(), self._get_brain_flow_input_parameters())
        return self._board

    def get_sampling_rate(self) -> int:
        if self._sampling_rate is None:
            self._sampling_rate = BoardShim.get_sampling_rate(self._get_board().board_id)
            Configuration.set_sampling_frequency(self._sampling_rate)
        return self._sampling_rate

    def get_eeg_channel_names(self) -> List[str]:
        if self._eeg_channel_names is None:
            self._eeg_channel_names = BoardShim.get_eeg_names(self._get_board().board_id)
        return self._eeg_channel_names

    def get_timestamp_channel(self) -> int:
        if self._timestamp_channel is None:
            self._timestamp_channel = BoardShim.get_timestamp_channel(self._get_board().board_id)
        return self._timestamp_channel

    def get_eeg_channels(self) -> List[int]:
        if self._eeg_channels is None:
            self._eeg_channels = BoardShim.get_eeg_channels(self._get_board().board_id)
        return self._eeg_channels

    def get_accelerometer_channels(self) -> List[int]:
        if self._accelerometer_channels is None:
            self._accelerometer_channels = BoardShim.get_accel_channels(self._get_board().board_id)
        return self._accelerometer_channels

    def open_session(self):
        self._get_board().prepare_session()

    def start_stream(self):
        if not self._get_board().is_prepared():
            self.open_session()
        self._get_board().start_stream()
        time.sleep(2)

    def get_data(self) -> BoardData:
        data = self._get_board().get_board_data()
        for count, channel in enumerate(self.get_eeg_channels()):
            self._preprocessing.process(data[channel])
        wrapped = BoardData(self.get_eeg_channel_names(), data[self.get_timestamp_channel()],
                            data[self.get_eeg_channels()], data[self.get_accelerometer_channels()])
        return wrapped

    def _stream_data_loop(self):
        while self._run_stream_loop:
            time.sleep(Configuration.get_open_bci_data_callback_frequency_ms() / 1000)
            self._data_callback(self.get_data())

    def start_data_loop(self):
        self._run_stream_loop = True
        self.start_stream()
        self._data_loop_thread.start()

    def set_data_callback(self, on_data_callback):
        self._data_callback = on_data_callback

    def start_stream_callback(self, on_data_callback):
        self.set_data_callback(on_data_callback)
        self.start_data_loop()

    def close_session(self):
        self._run_stream_loop = False
        self._data_loop_thread.join()
        self._get_board().stop_stream()
        self._get_board().release_session()
