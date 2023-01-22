import abc
from typing import Final, Dict

from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode
from typing import List


class OneHotToSingle(ProcessingNode):
    _MODULE_NAME: Final[str] = 'node.processing.encoder.onehottosingle'

    INPUT_MAIN: Final[str] = 'main'
    OUTPUT_MAIN: Final[str] = 'main'

    @abc.abstractmethod
    def _initialize_parameter_fields(self, parameters: dict):
        super()._initialize_parameter_fields(parameters)

    def _is_next_node_call_enabled(self) -> bool:
        return self._output_buffer[self.OUTPUT_MAIN].get_data_count() > 0

    def _is_processing_condition_satisfied(self) -> bool:
        return self._input_buffer[self.INPUT_MAIN].get_data_count() > 0

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        raw_data = data[self.INPUT_MAIN]
        encoded_data: FrameworkData = FrameworkData(sampling_frequency_hz=raw_data.sampling_frequency)
        for data_index in range(0, raw_data.get_data_count()):
            found_for_index = False
            for channel_index, channel in enumerate(raw_data.channels):
                if raw_data.get_data_at_index(data_index)[channel] > 0:
                    encoded_data.input_data_on_channel([channel_index])
                    found_for_index = True
                    break
            if not found_for_index:
                encoded_data.input_data_on_channel([0])
        return {
            self.OUTPUT_MAIN: encoded_data
        }

    def _get_inputs(self) -> List[str]:
        return [
            self.INPUT_MAIN
        ]

    def _get_outputs(self) -> List[str]:
        return [
            self.OUTPUT_MAIN
        ]
