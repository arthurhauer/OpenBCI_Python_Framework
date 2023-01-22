import abc
from typing import Final, Dict

from models.exception.non_compatible_data import NonCompatibleData
from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode
from typing import List


class SingleToOneHot(ProcessingNode):
    _MODULE_NAME: Final[str] = 'node.processing.encoder.singletoonehot'

    INPUT_MAIN: Final[str] = 'main'
    OUTPUT_MAIN: Final[str] = 'main'

    @abc.abstractmethod
    def _initialize_parameter_fields(self, parameters: dict):
        super()._initialize_parameter_fields(parameters)
        self.labels = parameters['labels']

    def _is_next_node_call_enabled(self) -> bool:
        return self._output_buffer[self.OUTPUT_MAIN].get_data_count() > 0

    def _is_processing_condition_satisfied(self) -> bool:
        return self._input_buffer[self.INPUT_MAIN].get_data_count() > 0

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        raw_data = data[self.INPUT_MAIN]
        if not raw_data.is_1d():
            raise NonCompatibleData(module=self._MODULE_NAME, cause='provided_data_is_multichannel')

        encoded_data: FrameworkData = FrameworkData(sampling_frequency_hz=raw_data.sampling_frequency,
                                                    channels=self.labels)
        for data_entry in raw_data.get_data_single_channel():
            for channel_index, channel in enumerate(self.labels):
                encoded_value = 1 if channel_index == data_entry else 0
                encoded_data.input_data_on_channel([encoded_value], channel)
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
