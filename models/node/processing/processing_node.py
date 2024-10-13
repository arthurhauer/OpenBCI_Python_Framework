import abc
import copy
from typing import List, Dict, Final

from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.node import Node


class ProcessingNode(Node):
    """
    A ProcessingNode is a type of Node that processes data from its input buffer to produce output data, based on its implemented
    processing logic. It extends the Node abstract class.

    Attributes:
        _MODULE_NAME (Final[str]): a constant string representing the name of the module where this class is defined.

    Methods:
        __init__(self, parameters=None):
            Initializes a ProcessingNode instance with the specified parameters.

        _validate_parameters(self, parameters: dict):
            Validates the specified parameters for the ProcessingNode instance, raising MissingParameterError if any required
            parameters are missing.

        _initialize_parameter_fields(self, parameters: dict):
            Initializes any custom parameter fields for the ProcessingNode instance.

        _initialize_buffer_options(self, buffer_options: dict) -> None:
            Initializes buffer behavior options for the ProcessingNode instance.

        _run(self, data: FrameworkData, input_name: str) -> None:
            Runs the ProcessingNode instance by inserting new input data, processing the input buffer, and outputting the processed
            data.

        _process_input_buffer(self):
            Processes the input buffer to produce output data.

        _is_next_node_call_enabled(self) -> bool:
            Returns True if the ProcessingNode instance allows the next node to be called, False otherwise.

        _is_processing_condition_satisfied(self) -> bool:
            Returns True if the processing condition for the ProcessingNode instance is satisfied, False otherwise.

        _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
            Processes the specified data to produce output data.

        _get_inputs(self) -> List[str]:
            Returns a list of input names for the ProcessingNode instance.

        _get_outputs(self) -> List[str]:
            Returns a list of output names for the ProcessingNode instance.

        dispose(self) -> None:
            Disposes of the ProcessingNode instance.
    """
    _MODULE_NAME: Final[str] = 'models.node.processing'

    def __init__(self, parameters=None) -> None:
        super().__init__(parameters=parameters)

    @abc.abstractmethod
    def _validate_parameters(self, parameters: dict):
        super()._validate_parameters(parameters)
        if 'clear_output_buffer_on_data_input' not in parameters['buffer_options']:
            raise MissingParameterError(
                module=self._MODULE_NAME,name=self.name,
                parameter='buffer_options.clear_output_buffer_on_data_input'
            )
        if 'clear_input_buffer_after_process' not in parameters['buffer_options']:
            raise MissingParameterError(
                module=self._MODULE_NAME,name=self.name,
                parameter='buffer_options.clear_input_buffer_after_process'
            )
        if 'clear_output_buffer_after_process' not in parameters['buffer_options']:
            raise MissingParameterError(
                module=self._MODULE_NAME,name=self.name,
                parameter='buffer_options.clear_output_buffer_after_process'
            )

    @abc.abstractmethod
    def _initialize_parameter_fields(self, parameters: dict):
        super()._initialize_parameter_fields(parameters)

    def _initialize_buffer_options(self, buffer_options: dict) -> None:
        """Processing node implementation of buffer behaviour options initialization

        :param buffer_options: Buffer behaviour options. Should contain bool attributes 'clear_output_buffer_on_data_input', 'clear_input_buffer_after_process' and 'clear_output_buffer_after_process'
        :type buffer_options: dict
        """
        self._clear_output_buffer_on_data_input = buffer_options['clear_output_buffer_on_data_input']
        self._clear_input_buffer_after_process = buffer_options['clear_input_buffer_after_process']
        self._clear_output_buffer_after_process = buffer_options['clear_output_buffer_after_process']

    def _run(self, data: FrameworkData, input_name: str) -> None:
        self.print(f'Inserting data in input buffer {input_name}')
        self._insert_new_input_data(data, input_name)
        if self._clear_output_buffer_on_data_input:
            self._clear_output_buffer()
        self._process_input_buffer()

    def _process_input_buffer(self):
        if not self._is_processing_condition_satisfied():
            return
        self.print('Starting processing of input buffer')
        processed_data = self._process(copy.deepcopy(self._input_buffer))
        if self._clear_input_buffer_after_process:
            self._clear_input_buffer()
        if self._clear_output_buffer_after_process:
            self._clear_output_buffer()
        self.print('Outputting data')
        for output_name in self._get_outputs():
            self._insert_new_output_data(processed_data[output_name], output_name)

    @abc.abstractmethod
    def _is_next_node_call_enabled(self) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def _is_processing_condition_satisfied(self) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        """Node self implementation of data processing, relating input and outputs.

        :param data: data to be processed.
        :type data: Dict[str,FrameworkData]
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def _get_inputs(self) -> List[str]:
        raise NotImplementedError()

    @abc.abstractmethod
    def _get_outputs(self) -> List[str]:
        raise NotImplementedError()

    def dispose(self) -> None:
        self._clear_input_buffer()
        self._clear_output_buffer()
        return
