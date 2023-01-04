import math

from typing import Final

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.processing.segmenter.segmenter import Segmenter


class FixedWindowSegmenter(Segmenter):
    _MODULE_NAME: Final[str] = 'node.processing.segmenter.fixedwindowsegmenter'

    def __init__(self, parameters: dict):
        super().__init__(parameters)
        self.window_size = parameters['window_size']
        self.filling_value = parameters['filling_value']

    def _is_processing_condition_satisfied(self) -> bool:
        return self._input_buffer[self.INPUT_MAIN].get_data_count() >= self.window_size

    def _validate_parameters(self, parameters: dict):
        if 'window_size' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME,
                                        parameter='window_size')
        if 'filling_value' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME,
                                        parameter='filling_type')
        if type(parameters['window_size']) is not int:
            raise InvalidParameterValue(module=self._MODULE_NAME,
                                        parameter='window_size',
                                        cause='must_be_int')
        if parameters['window_size'] < 1:
            raise InvalidParameterValue(module=self._MODULE_NAME,
                                        parameter='window_size',
                                        cause='must_be_greater_than_0')
        if type(parameters['filling_value']) is not str:
            raise InvalidParameterValue(module=self._MODULE_NAME,
                                        parameter='filling_value',
                                        cause='must_be_str')
        if parameters['filling_value'] not in ['zero', 'latest']:
            raise InvalidParameterValue(module=self._MODULE_NAME,
                                        parameter='filling_value',
                                        cause='must_be_in.[zero, latest]')

    def segment_data(self, data: FrameworkData) -> FrameworkData:
        segmented_data: FrameworkData = FrameworkData(sampling_frequency_hz=data.sampling_frequency)
        for channel in data.channels:
            raw_signal = data.get_data(channel)
            segmented_channel = []
            total_count = len(raw_signal)
            window_count = math.floor(total_count / self.window_size)
            remaining_samples = total_count % self.window_size
            for i in range(1, window_count+1):
                window_start = (i - 1) * self.window_size
                window_end = i * self.window_size
                current_window = raw_signal[window_start:window_end]
                segmented_channel.append(current_window)
            if remaining_samples > 0:
                window_start = window_count * self.window_size
                window_end = total_count - window_start
                fill_value = 0 if self.filling_value == 'zero' else raw_signal[total_count - 1]
                fill_count = window_count - remaining_samples
                current_window = raw_signal[window_start:window_end] + [fill_value] * fill_count
                segmented_channel.append(current_window)
            segmented_data.input_data_on_channel(segmented_channel, channel)
        return segmented_data
