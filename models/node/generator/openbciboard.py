from threading import Thread
from typing import Dict, List, Final

from brainflow import BrainFlowInputParams, BoardShim, BoardIds, LogLevels

from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.generator.generator_node import GeneratorNode
import time


class OpenBCIBoard(GeneratorNode):


    _MODULE_NAME: Final[str] = 'node.generator.open_bci_board'

    OUTPUT_EEG: Final[str] = 'eeg'
    OUTPUT_ACCELEROMETER: Final[str] = 'accelerometer'
    OUTPUT_TIMESTAMP: Final[str] = 'timestamp'

    def _validate_parameters(self, parameters: dict):
        super()._validate_parameters(parameters)
        if 'communication' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME,name=self.name,
                                        parameter='communication')
        if 'log_level' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME,name=self.name,
                                        parameter='log_level')
        if 'board' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME,name=self.name,
                                        parameter='board')

    def _initialize_parameter_fields(self, parameters: dict):
        super()._initialize_parameter_fields(parameters)
        self._board = None
        self._set_log_level(log_level=parameters['log_level'])
        self._set_brain_flow_input_parameters(parameters['communication'])
        self._get_board(board=parameters['board'])
        self._is_board_streaming = False
        self._eeg_channels = None
        self._eeg_channel_names = None
        self._accelerometer_channels = None
        self._accelerometer_channel_names = None
        self._timestamp_channel = None
        self._timestamp_channel_name = None
        self._sampling_rate = None
        self._data = []
        self._thread = Thread(target=self._get_data)
        self._stop_execution = False
        self._thread_started = False

    def _is_next_node_call_enabled(self) -> bool:
        return self._output_buffer[self.OUTPUT_TIMESTAMP].has_data()

    def _is_generate_data_condition_satisfied(self) -> bool:
        return True

    def _get_sampling_rate(self) -> int:
        if self._sampling_rate is None:
            self._sampling_rate = BoardShim.get_sampling_rate(self._get_board().board_id)
        return self._sampling_rate

    def _get_timestamp_channel(self) -> int:
        if self._timestamp_channel is None:
            self._timestamp_channel = BoardShim.get_timestamp_channel(self._get_board().board_id)
        return self._timestamp_channel

    def _get_timestamp_channel_name(self) -> str:
        if self._timestamp_channel_name is None:
            self._timestamp_channel_name = 'timestamp'
        return self._timestamp_channel_name

    def _get_eeg_channels(self) -> List[int]:
        if self._eeg_channels is None:
            self._eeg_channels = BoardShim.get_eeg_channels(self._get_board().board_id)
        return self._eeg_channels

    def _get_eeg_channel_names(self) -> List[str]:
        if self._eeg_channel_names is None:
            self._eeg_channel_names = BoardShim.get_eeg_names(self._get_board().board_id)
        return self._eeg_channel_names

    def _get_accelerometer_channels(self) -> List[int]:
        if self._accelerometer_channels is None:
            self._accelerometer_channels = BoardShim.get_accel_channels(self._get_board().board_id)
        return self._accelerometer_channels

    def _get_accelerometer_channel_names(self) -> List[str]:
        if self._accelerometer_channel_names is None:
            self._accelerometer_channel_names = ['x', 'y', 'z']
        return self._accelerometer_channel_names

    def _generate_data(self) -> Dict[str, FrameworkData]:
        if not self._thread_started:
            self.start()
        return_value = self._input_buffer.copy()
        self._clear_input_buffer()
        return return_value

    def _get_inputs(self) -> List[str]:
        return self._get_outputs()

    def _get_outputs(self) -> List[str]:
        return [
            self.OUTPUT_EEG,
            self.OUTPUT_ACCELEROMETER,
            self.OUTPUT_TIMESTAMP
        ]

    def start(self):
        self._thread_started = True
        self._stop_execution = False
        self._thread.start()

    def stop(self):
        if self._thread_started:
            self._thread_started = False
            self._stop_execution = True
            self._thread.join(1000)

    def dispose(self) -> None:
        self._get_board().stop_stream()
        self._get_board().release_session()
        self._is_board_streaming = False
        self._clear_output_buffer()
        self._clear_input_buffer()
        self.stop()

    @staticmethod
    def _set_log_level(log_level: str = "OFF"):
        if log_level is None:
            log_level = "OFF"
        log_level = "LEVEL_" + log_level
        BoardShim.set_log_level(LogLevels[log_level])

    @staticmethod
    def _get_board_type(board: str = "SYNTHETIC_BOARD") -> int:
        return BoardIds[board]

    def _set_brain_flow_input_parameters(self, parameters: dict):
        self._brain_flow_parameters = BrainFlowInputParams()
        if 'ip_port' in parameters:
            self._brain_flow_parameters.ip_port = parameters['ip_port']
        if 'mac_address' in parameters:
            self._brain_flow_parameters.mac_address = parameters['mac_address']
        if 'other_info' in parameters:
            self._brain_flow_parameters.other_info = parameters['other_info']
        if 'serial_number' in parameters:
            self._brain_flow_parameters.serial_number = parameters['serial_number']
        if 'ip_address' in parameters:
            self._brain_flow_parameters.ip_address = parameters['ip_address']
        if 'ip_protocol' in parameters:
            self._brain_flow_parameters.ip_protocol = parameters['ip_protocol']
        if 'timeout' in parameters:
            self._brain_flow_parameters.ip_protocol = parameters['timeout']
        if 'file' in parameters:
            self._brain_flow_parameters.file = parameters['file']
        if 'serial_port' in parameters:
            self._brain_flow_parameters.serial_port = parameters['serial_port']

    def _get_board(self, board: str = 'SYNTHETIC_BOARD') -> BoardShim:
        if self._board is None:
            self._board = BoardShim(self._get_board_type(board=board), self._brain_flow_parameters)
        return self._board

    def _start_stream(self):
        if not self._get_board().is_prepared():
            self._get_board().prepare_session()
        self._get_board().start_stream()
        time.sleep(2)
        self._is_board_streaming = True

    def _get_data(self):
        while True:
            if self._stop_execution:
                return

            if not self._is_board_streaming:
                self._start_stream()

            data = self._get_board().get_board_data()

            eeg_data = FrameworkData.from_multi_channel(
                self._get_sampling_rate(),
                self._get_eeg_channel_names(),
                data[self._get_eeg_channels()]
            )

            accelerometer_data = FrameworkData.from_multi_channel(
                self._get_sampling_rate(),
                self._get_accelerometer_channel_names(),
                data[self._get_accelerometer_channels()]
            )

            timestamp_data = FrameworkData.from_single_channel(
                self._get_sampling_rate(),
                data[self._get_timestamp_channel()]
            )

            self._insert_new_input_data(eeg_data, self.OUTPUT_EEG)
            self._insert_new_input_data(accelerometer_data, self.OUTPUT_ACCELEROMETER)
            self._insert_new_input_data(timestamp_data, self.OUTPUT_TIMESTAMP)

            time.sleep(1)
