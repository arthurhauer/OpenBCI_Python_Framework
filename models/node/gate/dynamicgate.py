import abc
from typing import Final

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.node.gate.gate_node import Gate


class DynamicGate(Gate):
    _MODULE_NAME: Final[str] = 'models.node.gate.dynamicgate'

    def __init__(self, parameters=None) -> None:
        super().__init__(parameters=parameters)

    @abc.abstractmethod
    def _validate_parameters(self, parameters: dict):
        super()._validate_parameters(parameters)
        if 'condition' not in parameters:
            raise MissingParameterError(
                module=self._MODULE_NAME, name=self.name,
                parameter='condition'
            )
        if type(parameters['condition']) is not str:
            raise InvalidParameterValue(
                module=self._MODULE_NAME, name=self.name,
                parameter='condition',
                cause='must_be_str'
            )

    @abc.abstractmethod
    def _initialize_parameter_fields(self, parameters: dict):
        super()._initialize_parameter_fields(parameters)
        condition = parameters['condition']
        self._condition_script = f'condition_result={condition}'

    def _initialize_buffer_options(self, buffer_options: dict) -> None:
        super()._initialize_buffer_options(buffer_options)

    @abc.abstractmethod
    def _check_gate_condition(self) -> bool:
        local_variables = {"condition_data": self._input_buffer[self.INPUT_CONDITION]}
        exec(self._condition_script, globals(), local_variables)
        condition_result = local_variables['condition_result']
        if type(condition_result) is not bool:
            raise InvalidParameterValue(
                module=self._MODULE_NAME,
                name=self.name,
                parameter='condition',
                cause='must_return_bool'
            )
        return condition_result
