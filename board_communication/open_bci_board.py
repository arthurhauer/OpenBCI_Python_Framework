from brainflow import BrainFlowInputParams, BoardShim, BoardIds
from nptyping import NDArray, Float

from board_communication.log_level import LogLevel
from config.configuration import Configuration


class OpenBCIBoard:
    _board: BoardShim

    def __init__(self) -> None:
        super().__init__()
        self._set_log_level()
        self._get_board()

    def _set_log_level(self):
        log_level = LogLevel[Configuration.get_open_bci_log_level()]
        if log_level is LogLevel.INFO:
            BoardShim.enable_board_logger()
        elif log_level is LogLevel.TRACE:
            BoardShim.enable_dev_board_logger()

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

    def _get_board(self):
        self._board = BoardShim(self._get_board_type(), self._get_brain_flow_input_parameters())

    def open_session(self):
        if self._board is None:
            self._get_board()
        self._board.prepare_session()

    def start_stream(self):
        if not self._board.is_prepared():
            self.open_session()
        self._board.start_stream()

    def close_session(self):
        self._board.stop_stream()
        self._board.release_session()

    def get_data(self) -> NDArray[Float]:
        return self._board.get_board_data()
