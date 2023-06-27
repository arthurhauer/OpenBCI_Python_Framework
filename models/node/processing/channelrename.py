from typing import List, Dict, Final

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode


class ChannelRename(ProcessingNode):
    _MODULE_NAME: Final[str] = 'node.processing.channel_rename'

    INPUT_MAIN: Final[str] = 'main'
    OUTPUT_MAIN: Final[str] = 'main'

    def _validate_parameters(self, parameters: dict):
        super()._validate_parameters(parameters)
        if 'dictionary' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='dictionary')
        if type(parameters['dictionary']) is not dict:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='split',
                                        cause='must_be_dict')
        if len(parameters['dictionary']) < 1:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='split',
                                        cause='must_be_have_at_least_1_key')
        for key in parameters['dictionary']:
            if type(key) is not str:
                raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                            parameter=f'split.{key}',
                                            cause='key_must_be_str')
            if type(parameters['dictionary'][key]) is not str:
                raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                            parameter=f'split.{key}',
                                            cause='value_must_be_str')

    def _initialize_parameter_fields(self, parameters: dict):
        super()._initialize_parameter_fields(parameters)
        self._rename_dictionary: Dict[str, str] = parameters['dictionary']

    def _is_next_node_call_enabled(self) -> bool:
        return self._output_buffer[self.OUTPUT_MAIN].get_data_count() > 0

    def _is_processing_condition_satisfied(self) -> bool:
        return self._input_buffer[self.INPUT_MAIN].get_data_count() > 0

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        renamed_data = data[self.INPUT_MAIN]
        for key in self._rename_dictionary:
            renamed_data.rename_channel(key, self._rename_dictionary[key])
        return {
            self.OUTPUT_MAIN: renamed_data
        }

    def _get_inputs(self) -> List[str]:
        return [
            self.INPUT_MAIN
        ]

    def _get_outputs(self) -> List[str]:
        return [
            self.OUTPUT_MAIN
        ]
