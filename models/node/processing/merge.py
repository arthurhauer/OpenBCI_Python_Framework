import statistics
import string
from random import random
from typing import List, Dict, Final

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.exception.non_compatible_data import NonCompatibleData
from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode


class Merge(ProcessingNode):
    _MODULE_NAME: Final[str] = 'node.processing.merge'

    INPUT_MASTER_MAIN: Final[str] = 'master_main'
    INPUT_MASTER_TIMESTAMP: Final[str] = 'master_timestamp'
    INPUT_SLAVE_MAIN: Final[str] = 'slave_main'
    INPUT_SLAVE_TIMESTAMP: Final[str] = 'slave_timestamp'
    OUTPUT_MERGED_MAIN: Final[str] = 'merged_main'
    OUTPUT_MERGED_TIMESTAMP: Final[str] = 'merged_timestamp'

    FILL_TYPE_ZEROFILL: Final[str] = 'zero_fill'
    FILL_TYPE_SAMPLE_AND_HOLD: Final[str] = 'sample_and_hold'

    def __init__(self, parameters: dict):
        super().__init__(parameters)

        self._sync_errors: List[float] = []
        if 'slave_filling' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME, parameter='slave_filling')

        if parameters['slave_filling'] not in [self.FILL_TYPE_ZEROFILL, self.FILL_TYPE_SAMPLE_AND_HOLD]:
            raise InvalidParameterValue(module=self._MODULE_NAME, parameter='slave_filling',
                                        cause=f'not_in_[{self.FILL_TYPE_ZEROFILL},{self.FILL_TYPE_SAMPLE_AND_HOLD}]')
        if 'statistics_enabled' not in parameters:
            parameters['statistics_enabled'] = False
        elif type(parameters['statistics_enabled']) is not bool:
            raise InvalidParameterValue(module=self._MODULE_NAME, parameter='statistics_enabled',
                                        cause='must_be_bool')

        self._statistics_enabled = parameters['statistics_enabled']
        self._zero_fill = parameters['slave_filling'] == self.FILL_TYPE_ZEROFILL
        self._sample_and_hold = parameters['slave_filling'] == self.FILL_TYPE_SAMPLE_AND_HOLD

    def _validate_parameters(self, parameters: dict):
        if 'slave_filling' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME,
                                        parameter='slave_filling')

        if parameters['slave_filling'] not in [self.FILL_TYPE_ZEROFILL, self.FILL_TYPE_SAMPLE_AND_HOLD]:
            raise InvalidParameterValue(module=self._MODULE_NAME,
                                        parameter='slave_filling',
                                        cause=f'not_in_[{self.FILL_TYPE_ZEROFILL},{self.FILL_TYPE_SAMPLE_AND_HOLD}]')
        if 'statistics_enabled' in parameters and type(parameters['statistics_enabled']) is not bool:
            raise InvalidParameterValue(module=self._MODULE_NAME,
                                        parameter='statistics_enabled',
                                        cause='must_be_bool')

    @classmethod
    def from_config_json(cls, parameters: dict):
        return cls(parameters)

    def _is_next_node_call_enabled(self) -> bool:
        return True

    def _is_processing_condition_satisfied(self) -> bool:
        return self._input_buffer[self.INPUT_SLAVE_TIMESTAMP].get_data_count() > 0 \
               and self._input_buffer[self.INPUT_MASTER_TIMESTAMP].get_data_count() > 0 \
               and (
                       self._input_buffer[self.INPUT_MASTER_TIMESTAMP].get_data_single_channel()[-1]
                       >= self._input_buffer[self.INPUT_SLAVE_TIMESTAMP].get_data_single_channel()[-1]
               )

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        lookup_start_index = 0
        print('Starting merge')
        master_main = data[self.INPUT_MASTER_MAIN]
        master_timestamp_data = data[self.INPUT_MASTER_TIMESTAMP].get_data_single_channel()
        slave_main = data[self.INPUT_SLAVE_MAIN]
        slave_timestamp = data[self.INPUT_SLAVE_TIMESTAMP]
        # Check if input data from master and slave have channels with the same name
        if not slave_main.get_channels_as_set().isdisjoint(master_main.channels):
            raise NonCompatibleData(self._MODULE_NAME, 'channels_with_same_name')

        new_slave_data = FrameworkData(sampling_frequency_hz=master_main.sampling_frequency,
                                       channels=slave_main.channels)

        for slave_timestamp_index, slave_timestamp_value in enumerate(slave_timestamp.get_data_single_channel()):
            closest_point = self._get_closest_timestamp_index_in_master(
                master_timestamp_data,
                slave_timestamp_value,
                lookup_start_index
            )
            new_slave_data.extend(
                self._fill(
                    lookup_start_index,
                    closest_point,
                    slave_main,
                    slave_timestamp_index,
                    master_main.sampling_frequency
                )
            )
            self._statistics(abs(master_timestamp_data[closest_point] - slave_timestamp_value) * 1000000)

            lookup_start_index = closest_point

        merged_data = FrameworkData()
        merged_data.extend(master_main)
        for channel in new_slave_data.channels:
            new_channel_name = channel
            if channel in merged_data.channels:
                rand_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                new_channel_name = f'{channel}{rand_id}'
            merged_data.input_data_on_channel(new_channel_name, new_slave_data.get_data(channel))
        return {
            self.OUTPUT_MERGED_MAIN: merged_data,
            self.OUTPUT_MERGED_TIMESTAMP: data[self.INPUT_MASTER_TIMESTAMP]
        }

    def _statistics(self, sync_error_microseconds: float):
        if self._statistics_enabled:
            self._sync_errors.append(sync_error_microseconds)
            print(f'---------------------------------------------------------------'
                  f'\nError is:\t\t\t\t{sync_error_microseconds} uS'
                  f'\nMean Error is:\t\t\t{statistics.mean(self._sync_errors)} uS'
                  f'\n---------------------------------------------------------------')

    def _get_inputs(self) -> List[str]:
        return [
            self.INPUT_MASTER_MAIN,
            self.INPUT_MASTER_TIMESTAMP,
            self.INPUT_SLAVE_MAIN,
            self.INPUT_SLAVE_TIMESTAMP,
        ]

    def _get_outputs(self) -> List[str]:
        return [
            self.OUTPUT_MERGED_MAIN,
            self.OUTPUT_MERGED_TIMESTAMP
        ]

    @staticmethod
    def _get_closest_timestamp_index_in_master(master_timestamp: List[float],
                                               slave_timestamp: float,
                                               lookup_start_index: int = 0,
                                               ) -> int:
        filtered: List[float] = master_timestamp[lookup_start_index::]
        closest_point: int = min(range(len(filtered)), key=lambda i: abs(filtered[i] - slave_timestamp))
        return closest_point

    def _fill(self,
              start_index: int,
              end_index: int,
              slave_main: FrameworkData,
              slave_main_value_index: int,
              master_sampling_frequency: float) -> FrameworkData:
        fill_data = FrameworkData(master_sampling_frequency, slave_main.channels)
        fill_size = (end_index - start_index)
        if self._zero_fill:
            channel_data = [0] * fill_size
            input_data = [channel_data] * len(slave_main.channels)
            fill_data.input_2d_data(input_data)
        elif self._sample_and_hold:
            input_data = slave_main.get_data_at_index(slave_main_value_index)
            for channel in input_data:
                channel_data = [input_data[channel]] * fill_size
                fill_data.input_data_on_channel(channel, channel_data)
        else:
            raise InvalidParameterValue(module=self._MODULE_NAME,
                                        parameter='slave_filling',
                                        cause='not_set')

        return fill_data
