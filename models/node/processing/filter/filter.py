import abc
from typing import List, Dict, Final, Tuple
from scipy.signal import lfilter
from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode


class Filter(ProcessingNode):
    _MODULE_NAME: Final[str] = 'node.processing.filter.filter'

    INPUT_MAIN: Final[str] = 'main'
    OUTPUT_MAIN: Final[str] = 'main'

    @abc.abstractmethod
    def _validate_parameters(self, parameters: dict):
        super()._validate_parameters(parameters)

    @abc.abstractmethod
    def _initialize_parameter_fields(self, parameters: dict):
        super()._initialize_parameter_fields(parameters)

    def _set_filter(self, sampling_frequency_hz: float) -> None:
        self._filter_numerator, self._filter_denominator = self._get_filter_coefficients(self.parameters,
                                                                                         sampling_frequency_hz)

    @abc.abstractmethod
    def _get_filter_coefficients(self, parameters: dict, sampling_frequency_hz: float) -> Tuple[list, list]:
        raise NotImplementedError()

    def _is_next_node_call_enabled(self) -> bool:
        return True

    def _is_processing_condition_satisfied(self) -> bool:
        return self._input_buffer[self.INPUT_MAIN].get_data_count() > 0

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        filtered_data: Dict[str, FrameworkData] = {}
        for key in data:
            filtered_data[key] = FrameworkData(sampling_frequency_hz=data[key].sampling_frequency)
            b, a = self._get_filter_coefficients(self.parameters, data[key].sampling_frequency)
            for channel in data[key].channels:
                raw_signal = data[key].get_data(channel)
                filtered_signal = lfilter(b, a, raw_signal)
                filtered_data[key].input_data_on_channel(filtered_signal, channel)

        return filtered_data

    def _get_inputs(self) -> List[str]:
        return [
            self.INPUT_MAIN
        ]

    def _get_outputs(self) -> List[str]:
        return [
            self.OUTPUT_MAIN
        ]
