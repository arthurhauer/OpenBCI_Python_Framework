import abc
from typing import List, Dict

from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.node import Node


class OutputNode(Node):
    """ This is the base class for all output nodes. It is responsible for validating the parameters that 
    were passed to the node, and for initializing the parameters that were passed to the node. It should
    not be used directly, but rather, it should be inherited by all output nodes.

    :param parameters: The parameters that were passed to the node.
    :type parameters: dict
    """

    def __init__(self, parameters: dict):
        super().__init__(parameters=parameters)

    @abc.abstractmethod
    def _validate_parameters(self, parameters: dict) -> None:
        """ Validates the parameters that were passed to the node.
        """
        parameters['outputs']={}
        super()._validate_parameters(parameters)
        if 'clear_output_buffer_on_data_input' not in parameters['buffer_options']:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='buffer_options.clear_output_buffer_on_data_input')
        if 'clear_input_buffer_after_process' not in parameters['buffer_options']:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='buffer_options.clear_input_buffer_after_process')
        if 'clear_output_buffer_after_process' not in parameters['buffer_options']:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='buffer_options.clear_output_buffer_after_process')

    def _run(self, data: FrameworkData, input_name: str) -> None:
        self.print(f'Inserting data in input buffer {input_name}')
        self._insert_new_input_data(data, input_name)
        if self._clear_output_buffer_on_data_input:
            self._clear_output_buffer()
        self._process_input_buffer()

    def _process_input_buffer(self) -> None:
        if not self._is_processing_condition_satisfied():
            return
        self.print('Starting processing of input buffer')
        self._process(self._input_buffer)
        if self._clear_input_buffer_after_process:
            self._clear_input_buffer()
        if self._clear_output_buffer_after_process:
            self._clear_output_buffer()


    @abc.abstractmethod
    def _process(self, data: Dict[str, FrameworkData]) -> None:
        """Node self implementation of data processing, relating input.

        :param data: data to be processed.
        :type data: Dict[str,FrameworkData]
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def _is_processing_condition_satisfied(self) -> bool:
        """ Runs the node accordingly to the output node's logic.
        """
        raise NotImplementedError()

    def _is_next_node_call_enabled(self) -> bool:
        """ Returns whether the next node call is enabled or not.
        """
        return False

    def _initialize_buffer_options(self, buffer_options: dict) -> None:
        """ Initializes the buffer options based on the parameters that were passed to the node.
        """
        self._clear_output_buffer_on_data_input = buffer_options['clear_output_buffer_on_data_input']
        self._clear_input_buffer_after_process = buffer_options['clear_input_buffer_after_process']
        self._clear_output_buffer_after_process = buffer_options['clear_output_buffer_after_process']


    @abc.abstractmethod
    def _get_inputs(self) -> List[str]:
        """ Returns the input names of this node.
        """
        raise NotImplementedError()

    def _get_outputs(self) -> List[str]:
        """ Returns the output names of this node.
        """
        return []

    def _build_graph_outputs(self):
        return ''

    def dispose(self) -> None:
        """ Node self disposal  of disposal of allocated resources.
        """
        super().dispose()
