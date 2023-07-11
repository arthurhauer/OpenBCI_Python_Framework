import statistics
from typing import List, Dict, Final

import numpy as np

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode


class EpochStatistics(ProcessingNode):
    _MODULE_NAME: Final[str] = 'node.processing.epochstatistics'

    _ALLOWED_METHODS: Final[List[str]] = ['fmean', 'geometric_mean', 'harmonic_mean', 'mean', 'median',
                                          'median_grouped', 'median_high', 'median_low', 'mode',
                                          'pstdev', 'pvariance', 'stdev', 'variance']
    INPUT_MAIN: Final[str] = 'main'
    OUTPUT_MAIN: Final[str] = 'main'

    def _validate_parameters(self, parameters: dict):
        super()._validate_parameters(parameters)
        if 'statistic' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='statistic')
        if type(parameters['statistic']) is not str:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='statistic',
                                        cause='must_be_string')
        if parameters['statistic'] not in self._ALLOWED_METHODS:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='statistic',
                                        cause=f'must_be_one_of_{self._ALLOWED_METHODS}')

    def _initialize_parameter_fields(self, parameters: dict):
        super()._initialize_parameter_fields(parameters)
        self._statistic_func = getattr(statistics, parameters['statistic'])

    def _is_next_node_call_enabled(self) -> bool:
        return self._output_buffer[self.OUTPUT_MAIN].get_data_count() > 0

    def _is_processing_condition_satisfied(self) -> bool:
        return self._input_buffer[self.INPUT_MAIN].get_data_count() > 0

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        input_data = data[self.INPUT_MAIN]
        return_data: FrameworkData = FrameworkData(input_data.sampling_frequency,
                                                   input_data.channels)
        for channel in input_data.channels:
            formatted_data = []
            for epoch in input_data.get_data_on_channel(channel):
                formatted_data.append(self._statistic_func(epoch))
            return_data.input_data_on_channel(np.asarray(formatted_data), channel)
        return {
            self.OUTPUT_MAIN: return_data
        }

    def _get_inputs(self) -> List[str]:
        """ This method returns the inputs of the node. In this case it returns a single 'main' input.
        """
        return [
            self.INPUT_MAIN
        ]

    def _get_outputs(self) -> List[str]:
        """ This method returns the outputs of the node. In this case it returns a single 'main' output.
        """
        return [
            self.OUTPUT_MAIN
        ]
