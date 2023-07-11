from threading import Thread
from typing import Dict, List, Final

from brainflow import BrainFlowInputParams, BoardShim, BoardIds, LogLevels

from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.generator.generator_node import GeneratorNode
import time


class OpenBCIBoard(GeneratorNode):
    """ This node is used to connect to an OpenBCI board and collect data from it.
    The node is based on the BrainFlow library and it is compatible with all the boards
    supported by the library. The node is able to connect to the board all BrainFlow
    supported communication methods:\n
        - Wifi;
        - Bluetooth;
        - USB;
        - Synthetic board (for testing purposes).
    
    The node is able to collect data from the board and send it to the next node in the pipeline.

    Attributes:
        _MODULE_NAME (str): The name of the module (in this case, ``models.node.generator.open_bci_board``).
        OUTPUT_EEG (str): Output data type (in this case, ``eeg``).
        OUTPUT_ACCELEROMETER (str): The name of the output containing the accelerometer data (in this case, ``accelerometer``).
        OUTPUT_TIMESTAMP (str): The name of the output containing the timestamp data (in this case, ``timestamp``).
    
    ``configuration.json`` usage:

        **module** (*str*): Current module name (in this case ``models.node.generator``).\n
        **type** (*str*): Current node type (in this case ``OpenBCIBoard``).\n
        **communication** (*dict*): OpenBCIBoard communication parameters.\n
            **ip_port** (*int*): ip port for socket connection, for some boards where we know it in front you dont need this parameter (default: ``0``).\n
            **mac_address** (*str*): mac address for example its used for bluetooth based boards, if not provided BrainFlow will try to autodiscover the device (default: ``""``).\n
            **other_info** (*str*): other info, for example it can be ip address for wifi shield (default: ``""``).\n
            **serial_number** (*str*): serial number of device. Important if you have multiple devices in the same place. If not provided BrainFlow will try to autodiscover the device (default: ``""``).\n
            **ip_address** (*str*): ip address is used for boards which reads data from socket connection (default: ``""``).\n
            **ip_protocol** (*int*): ip protocol type from IpProtocolType enum from brainflow lib (default: ``IpProtocolType.NONE.value``).\n
            **timeout** (*int*): timeout for device discovery (default: ``0``).\n
            **file** (*str*): file is used for file boards (default: ``""``).\n
            **serial_port** (*str*): serial port, e.g. COM4, /dev/ttyACM0, etc (default: ``""``).\n
        **log_level** (*str*): The log level of the node (default: ``"OFF"``).\n
        **board** (*str*): The type of the board (default: ``"SYNTHETIC_BOARD"``). Check all the supported boards in https://brainflow.readthedocs.io/en/stable/SupportedBoards.html#supported-boards-label.\n
        **buffer_options** (*dict*): Buffer options.\n
            **clear_output_buffer_on_generate** (*bool*): If ``True``, the output buffer will be cleared when the node is executed.\n
    """

    _MODULE_NAME: Final[str] = 'node.generator.open_bci_board'

    OUTPUT_EEG: Final[str] = 'eeg'
    OUTPUT_ACCELEROMETER: Final[str] = 'accelerometer'
    OUTPUT_TIMESTAMP: Final[str] = 'timestamp'

    def _validate_parameters(self, parameters: dict):
        """ Validates the specified parameters for the OpenBCIBoard instance, raising MissingParameterError if any required
        parameters are missing.

        :param parameters: The parameters to validate.
        :type parameters: dict
        
        :raises MissingParameterError: the ``communication`` parameter is required.
        :raises MissingParameterError: the ``log_level`` parameter is required.
        :raises MissingParameterError: the ``board`` parameter is required.
        """

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
        """ Initializes the fields of the OpenBCIBoard instance.

        :param parameters: The parameters to initialize the fields.
        :type parameters: dict
        """
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
        """ Returns ``True`` if the next node call is enabled, ``False`` otherwise.
        """
        return self._output_buffer[self.OUTPUT_TIMESTAMP].has_data()

    def _is_generate_data_condition_satisfied(self) -> bool:
        return True

    def _get_sampling_rate(self) -> int:
        """ Returns the sampling rate of the board.
        """
        if self._sampling_rate is None:
            self._sampling_rate = BoardShim.get_sampling_rate(self._get_board().board_id)
        return self._sampling_rate

    def _get_timestamp_channel(self) -> int:
        """ Returns the timestamp channel of the board.
        """
        if self._timestamp_channel is None:
            self._timestamp_channel = BoardShim.get_timestamp_channel(self._get_board().board_id)
        return self._timestamp_channel

    def _get_timestamp_channel_name(self) -> str:
        """ Returns the name of the timestamp channel of the board.
        """
        if self._timestamp_channel_name is None:
            self._timestamp_channel_name = 'timestamp'
        return self._timestamp_channel_name

    def _get_eeg_channels(self) -> List[int]:
        """ Returns the EEG channels of the board.
        """
        if self._eeg_channels is None:
            self._eeg_channels = BoardShim.get_eeg_channels(self._get_board().board_id)
        return self._eeg_channels

    def _get_eeg_channel_names(self) -> List[str]:
        """ Returns the names of the EEG channels of the board.
        """
        if self._eeg_channel_names is None:
            self._eeg_channel_names = BoardShim.get_eeg_names(self._get_board().board_id)
        return self._eeg_channel_names

    def _get_accelerometer_channels(self) -> List[int]:
        """ Returns the accelerometer channels of the board.
        """
        if self._accelerometer_channels is None:
            self._accelerometer_channels = BoardShim.get_accel_channels(self._get_board().board_id)
        return self._accelerometer_channels

    def _get_accelerometer_channel_names(self) -> List[str]:
        """ Returns the names of the accelerometer channels of the board.
        """
        if self._accelerometer_channel_names is None:
            self._accelerometer_channel_names = ['x', 'y', 'z']
        return self._accelerometer_channel_names

    def _generate_data(self) -> Dict[str, FrameworkData]:
        """ Generates data for the next trial. This method is called by the node when it is executed.
        """
        if not self._thread_started:
            self.start()
        return_value = self._input_buffer.copy()
        self._clear_input_buffer()
        return return_value

    def _get_inputs(self) -> List[str]:
        """ Returns the inputs of the node.
        """
        return self._get_outputs()

    def _get_outputs(self) -> List[str]:
        """ Returns the outputs of the node.
        """
        return [
            self.OUTPUT_EEG,
            self.OUTPUT_ACCELEROMETER,
            self.OUTPUT_TIMESTAMP
        ]

    def start(self):
        """ Starts the thread that collects data from the board.
        """
        self._thread_started = True
        self._stop_execution = False
        self._thread.start()

    def stop(self):
        """ Stops the thread that collects data from the board.
        """
        if self._thread_started:
            self._thread_started = False
            self._stop_execution = True
            self._thread.join(1000)

    def dispose(self) -> None:
        """ Node self implementation of disposal of allocated resources.
        """
        self._get_board().stop_stream()
        self._get_board().release_session()
        self._is_board_streaming = False
        self._clear_output_buffer()
        self._clear_input_buffer()
        self.stop()

    @staticmethod
    def _set_log_level(log_level: str = "OFF"):
        """ Sets the log level of the node.

        :param log_level: The log level to set(default: ``"OFF"``).
        :type log_level: str
        """
        if log_level is None:
            log_level = "OFF"
        log_level = "LEVEL_" + log_level
        BoardShim.set_log_level(LogLevels[log_level])

    @staticmethod
    def _get_board_type(board: str = "SYNTHETIC_BOARD") -> int:
        """ Returns the board type.

        :param board: The board type(default: ``"SYNTHETIC_BOARD"``).
        :type board: str
        """
        return BoardIds[board]

    def _set_brain_flow_input_parameters(self, parameters: dict):
        """ Sets the BrainFlowInputParameters of the node.

        :param parameters: The parameters to set.
        :type parameters: dict
        """
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
        """ Returns the board instance.

        :param board: The board type(default: ``"SYNTHETIC_BOARD"``).
        :type board: str

        :return: The board instance.
        :rtype: BoardShim
        """
        if self._board is None:
            self._board = BoardShim(self._get_board_type(board=board), self._brain_flow_parameters)
        return self._board

    def _start_stream(self):
        """ Starts the stream of the board. This method is start streaming thread and store data in internal ringbuffer.

        """
        if not self._get_board().is_prepared():
            self._get_board().prepare_session()
        self._get_board().start_stream()
        time.sleep(5)
        self._is_board_streaming = True

    def _get_data(self):
        """ Collects data from the board. This method get the data from ringbuffer, create a FrameworkData instance
        and insert it in the Node output buffer.
        """
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

    def build_graphviz_representation(self):
        return f"""
        {self.name} [
      shape=plaintext
      tooltip="{self.parameters}"
      label=<
            <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="0">
               {self._build_graph_inputs()}
               <TR>
                  <TD BORDER="1" STYLE="ROUNDED" CELLPADDING="4" COLOR="black">{self.name}<BR/><FONT POINT-SIZE="5">{self._MODULE_NAME}</FONT><BR/><FONT POINT-SIZE="5">{self._get_eeg_channel_names()}</FONT></TD>
               </TR>
               {self._build_graph_outputs()}
            </TABLE>
        >
      ];
        """
