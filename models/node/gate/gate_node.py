import abc
from typing import List, Final

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.node import Node


class Gate(Node):
    _MODULE_NAME: Final[str] = 'models.node.gate'

    INPUT_CONDITION: Final[str] = 'condition'
    INPUT_SIGNAL: Final[str] = 'signal'
    OUTPUT_MAIN: Final[str] = 'main'

    def __init__(self, parameters=None) -> None:
        super().__init__(parameters=parameters)

    def _validate_parameters(self, parameters: dict):
        super()._validate_parameters(parameters)
        if 'clear_input_buffer_if_condition_not_met' not in parameters['buffer_options']:
            raise MissingParameterError(
                module=self._MODULE_NAME,
                name=self.name,
                parameter='buffer_options.clear_input_buffer_if_condition_not_met'
            )
        if type(parameters['buffer_options']['clear_input_buffer_if_condition_not_met']) is not bool:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='buffer_options.clear_input_buffer_if_condition_not_met',
                                        cause='must_be_bool')
        if 'clear_output_buffer_if_condition_met' not in parameters['buffer_options']:
            raise MissingParameterError(
                module=self._MODULE_NAME,
                name=self.name,
                parameter='buffer_options.clear_output_buffer_if_condition_met'
            )
        if type(parameters['buffer_options']['clear_output_buffer_if_condition_met']) is not bool:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='buffer_options.clear_output_buffer_if_condition_met',
                                        cause='must_be_bool')

    @abc.abstractmethod
    def _initialize_parameter_fields(self, parameters: dict):
        super()._initialize_parameter_fields(parameters)

    def _initialize_buffer_options(self, buffer_options: dict) -> None:
        """Gate node implementation of buffer behaviour options initialization

        :param buffer_options: Buffer behaviour options. Should contain bool attributes 'clear_input_buffer_if_condition_not_met' and 'clear_output_buffer_if_condition_met'
        :type buffer_options: dict
        """
        self.clear_input_buffer_if_condition_not_met = buffer_options['clear_input_buffer_if_condition_not_met']
        self.clear_output_buffer_if_condition_met = buffer_options['clear_output_buffer_if_condition_met']

    def _run(self, data: FrameworkData, input_name: str) -> None:
        self.print(f'Inserting data in input buffer {input_name}')
        self._insert_new_input_data(data, input_name)
        gate_bypass_condition_met = self._check_gate_condition()
        if not gate_bypass_condition_met:
            if self.clear_input_buffer_if_condition_not_met:
                self.print('Clearing input buffer because condition was not met')
                self._clear_input_buffer()
            return
        if self.clear_output_buffer_if_condition_met:
            self.print('Clearing output buffer because condition was met')
            self._clear_output_buffer()
        self._insert_new_output_data(self._input_buffer[self.INPUT_SIGNAL], self.OUTPUT_MAIN)

    @abc.abstractmethod
    def _check_gate_condition(self) -> bool:
        raise NotImplementedError()

    def _is_next_node_call_enabled(self) -> bool:
        return self._output_buffer[self.OUTPUT_MAIN].get_data_count() > 0

    def _get_inputs(self) -> List[str]:
        return [
            self.INPUT_CONDITION,
            self.INPUT_SIGNAL
        ]

    def _get_outputs(self) -> List[str]:
        return [
            self.OUTPUT_MAIN
        ]

    def dispose(self) -> None:
        self._clear_input_buffer()
        self._clear_output_buffer()
        return
