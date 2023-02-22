from typing import List, Dict, Final

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode


class Fill(ProcessingNode):
    _MODULE_NAME: Final[str] = 'node.processing.fill'

    INPUT_MAIN: Final[str] = 'main'
    OUTPUT_MAIN: Final[str] = 'main'

    FILL_TYPE_ZEROFILL: Final[str] = 'zero_fill'
    FILL_TYPE_SAMPLE_AND_HOLD: Final[str] = 'sample_and_hold'

    def _validate_parameters(self, parameters: dict):

        if 'fill_size' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='fill_size')
        if 'filling_type' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='filling_type')

        if type(parameters['fill_size']) is not int:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='fill_size',
                                        cause='must_be_int')

        if parameters['filling_type'] not in [self.FILL_TYPE_ZEROFILL, self.FILL_TYPE_SAMPLE_AND_HOLD]:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='filling_type',
                                        cause=f'not_in_[{self.FILL_TYPE_ZEROFILL},{self.FILL_TYPE_SAMPLE_AND_HOLD}]')

    def _initialize_parameter_fields(self, parameters: dict):
        super()._initialize_parameter_fields(parameters)
        self._zero_fill = parameters['filling_type'] == self.FILL_TYPE_ZEROFILL
        self._sample_and_hold = parameters['filling_type'] == self.FILL_TYPE_SAMPLE_AND_HOLD
        self._fill_size: int = parameters['fill_size']

    def _is_next_node_call_enabled(self) -> bool:
        return True

    def _is_processing_condition_satisfied(self) -> bool:
        return self._input_buffer[self.INPUT_MAIN].get_data_count() > 0

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        slave_main = data[self.INPUT_MAIN]

        new_data = FrameworkData(sampling_frequency_hz=slave_main.sampling_frequency,
                                 channels=slave_main.channels)

        for data_index, data_value in enumerate(slave_main.get_data_as_2d_array()[0]):
            new_data.extend(
                self._fill(
                    data_index,
                    slave_main,
                    new_data.sampling_frequency
                )
            )
        return {
            self.OUTPUT_MAIN: new_data
        }

    def _get_inputs(self) -> List[str]:
        return [
            self.INPUT_MAIN,
        ]

    def _get_outputs(self) -> List[str]:
        return [
            self.OUTPUT_MAIN
        ]

    def _fill(self,
              data_index: int,
              slave_main: FrameworkData,
              sampling_frequency: float) -> FrameworkData:
        fill_data = FrameworkData(sampling_frequency, slave_main.channels)

        if self._zero_fill:
            channel_data = [0] * self._fill_size
            input_data = [channel_data] * len(slave_main.channels)
            fill_data.input_2d_data(input_data)
        elif self._sample_and_hold:
            input_data = slave_main.get_data_at_index(data_index)
            for channel in input_data:
                channel_data = [input_data[channel]] * self._fill_size
                fill_data.input_data_on_channel(channel_data, channel)
        else:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='filling_type',
                                        cause='not_set')

        return fill_data
