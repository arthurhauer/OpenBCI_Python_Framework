from typing import Dict, List, Final

from brainflow import BrainFlowInputParams, BoardShim, BoardIds, LogLevels
from models.node.generator.generator_node import GeneratorNode
import time


class OpenBCIBoard(GeneratorNode):
    OUTPUT_EEG: Final[str] = 'eeg'
    OUTPUT_ACCELEROMETER: Final[str] = 'accelerometer'
    OUTPUT_TIMESTAMP: Final[str] = 'timestamp'

    def __init__(self,
                 parameters: dict,
                 ) -> None:
        super().__init__(parameters)
        if 'communication' not in parameters:
            raise ValueError('error'
                             '.missing'
                             '.node'
                             '.generator'
                             '.open_bci_board'
                             '.communication')
        if 'log_level' not in parameters:
            raise ValueError('error'
                             '.missing'
                             '.node'
                             '.generator'
                             '.open_bci_board'
                             '.log_level')
        if 'board' not in parameters:
            raise ValueError('error'
                             '.missing'
                             '.node'
                             '.generator'
                             '.open_bci_board'
                             '.board')
        self._board = None
        self._set_log_level(log_level=parameters['log_level'])
        self._set_brain_flow_input_parameters(parameters['communication'])
        self._get_board(board=parameters['board'])
        self._is_board_streaming = False
        self._eeg_channels = None
        self._accelerometer_channels = None
        self._timestamp_channel = None

    @classmethod
    def from_config_json(cls, parameters: dict):
        board = cls(
            parameters=parameters
        )
        return board

    def _is_next_node_call_enabled(self) -> bool:
        return True

    def _is_generate_data_condition_satisfied(self) -> bool:
        return True

    def _get_timestamp_channel(self) -> int:
        if self._timestamp_channel is None:
            self._timestamp_channel = BoardShim.get_timestamp_channel(self._get_board().board_id)
        return self._timestamp_channel

    def _get_eeg_channels(self) -> List[int]:
        if self._eeg_channels is None:
            self._eeg_channels = BoardShim.get_eeg_channels(self._get_board().board_id)
        return self._eeg_channels

    def _get_accelerometer_channels(self) -> List[int]:
        if self._accelerometer_channels is None:
            self._accelerometer_channels = BoardShim.get_accel_channels(self._get_board().board_id)
        return self._accelerometer_channels

    def _generate_data(self) -> Dict[str, list]:
        if not self._is_board_streaming:
            self._start_stream()
        data = self._get_board().get_board_data()
        return {
            self.OUTPUT_EEG: data[self._get_eeg_channels()],
            self.OUTPUT_ACCELEROMETER: data[self._get_accelerometer_channels()],
            self.OUTPUT_TIMESTAMP: data[self._get_timestamp_channel()]
        }

    def _get_outputs(self) -> List[str]:
        return [
            self.OUTPUT_EEG,
            self.OUTPUT_ACCELEROMETER,
            self.OUTPUT_TIMESTAMP
        ]

    def dispose(self) -> None:
        self._get_board().stop_stream()
        self._get_board().release_session()
        self._is_board_streaming = False

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
