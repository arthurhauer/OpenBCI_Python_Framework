from brainflow import BrainFlowInputParams, BoardShim, BoardIds, LogLevels
from models.node.generator.generator_node import GeneratorNode
import time


class OpenBCIBoard(GeneratorNode):

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

    def _generate_data(self) -> list:
        if not self._is_board_streaming:
            self._start_stream()
        data = self._get_board().get_board_data()
        return list(map(list, zip(*data)))

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
