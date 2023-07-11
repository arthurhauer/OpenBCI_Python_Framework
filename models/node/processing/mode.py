from statistics import mode
from typing import List, Dict, Final

import numpy as np

from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode


class Mode(ProcessingNode):
    _MODULE_NAME: Final[str] = 'node.processing.mode'

    INPUT_MAIN: Final[str] = 'main'
    OUTPUT_MAIN: Final[str] = 'main'

    def _validate_parameters(self, parameters: dict):
        super()._validate_parameters(parameters)

    def _initialize_parameter_fields(self, parameters: dict):
        super()._initialize_parameter_fields(parameters)

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
                formatted_data.append(mode(epoch))
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
