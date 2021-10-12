from threading import Thread

import time
from brainflow import BrainFlowInputParams, BoardShim, BoardIds, LogLevels
from nptyping import NDArray, Float

from board_communication.models.board_data import BoardData
from config.configuration import Configuration


class OpenBCIBoard:
    def __init__(self) -> None:
        super().__init__()
        self._board = None
        self._eeg_channels = None
        self._accelerometer_channels = None
        self._set_log_level()
        self._get_board()
        self._get_eeg_channels()
        self._get_accelerometer_channels()
        self._run_stream_loop: bool = False
        self._data_loop_thread: Thread = Thread(target=self._stream_data_loop)
        self._data_callback = None

    def _set_log_level(self):
        log_level = Configuration.get_open_bci_log_level()
        if log_level is None:
            log_level = "OFF"
        log_level = "LEVEL_" + log_level
        BoardShim.set_log_level(LogLevels[log_level])

    def _get_board_type(self) -> int:
        return BoardIds[Configuration.get_open_bci_board()]

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

    def _get_eeg_channels(self) -> list:
        if self._eeg_channels is None:
            self._eeg_channels = BoardShim.get_eeg_channels(self._get_board().board_id)
        return self._eeg_channels

    def _get_accelerometer_channels(self) -> list:
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
        data = BoardData()
        data.append_data(self._get_board().get_board_data(), self._get_eeg_channels(),
                         self._get_accelerometer_channels())
        return data

    def _stream_data_loop(self):
        while self._run_stream_loop:
            time.sleep(1)
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
