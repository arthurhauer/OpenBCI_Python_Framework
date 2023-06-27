import abc
import string
from random import random
from typing import List, Dict, Final

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode
from models.node.processing.synchronize import Synchronize


class Split(ProcessingNode):
    _MODULE_NAME: Final[str] = 'node.processing.split'

    INPUT_MAIN: Final[str] = 'main'

    @abc.abstractmethod
    def _validate_parameters(self, parameters: dict):
        super()._validate_parameters(parameters)
        if 'split' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='split')
        if type(parameters['split']) is not dict:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='split',
                                        cause='must_be_dict')
        if len(parameters['split']) < 2:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='split',
                                        cause='must_be_have_at_least_2_keys')
        for key in parameters['split']:
            if type(parameters['split'][key]) is not list:
                raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                            parameter=f'split.{key}',
                                            cause='must_be_list')
            if len(parameters['split'][key]) < 1:
                raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                            parameter=f'split.{key}',
                                            cause='must_not_be_empty')
            for channel in parameters['split'][key]:
                if type(channel) is not str:
                    raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                                parameter=f'split.{key}.{channel}',
                                                cause='must_be_str')

    @abc.abstractmethod
    def _initialize_parameter_fields(self, parameters: dict):
        super()._initialize_parameter_fields(parameters)
        self._outputs: List[str] = list(parameters['split'].keys())
        self._split: Dict[str, List[str]] = parameters['split']

    def _is_next_node_call_enabled(self) -> bool:
        return True

    def _is_processing_condition_satisfied(self) -> bool:
        condition: bool = True
        for key in self._split:
            for channel in self._split[key]:
                condition = condition and len(self._input_buffer[self.INPUT_MAIN].get_data_on_channel(channel)) > 0
        return condition

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        input_data = data[self.INPUT_MAIN]
        return_dict: Dict[str, FrameworkData] = {}
        for key in self._split:
            channels: List[str] = self._split[key]
            return_dict[key] = FrameworkData(input_data.sampling_frequency, channels)
            for channel in channels:
                return_dict[key].input_data_on_channel(input_data.get_data_on_channel(channel), channel)
        return return_dict

    def _get_inputs(self) -> List[str]:
        return [
            self.INPUT_MAIN
        ]

    def _get_outputs(self) -> List[str]:
        return self._outputs
