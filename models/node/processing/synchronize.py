import statistics
import copy
from typing import List, Dict, Final
from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode


class Synchronize(ProcessingNode):
    _MODULE_NAME: Final[str] = 'node.processing.synchronize'

    INPUT_MASTER_MAIN: Final[str] = 'master_main'
    INPUT_MASTER_TIMESTAMP: Final[str] = 'master_timestamp'
    INPUT_SLAVE_MAIN: Final[str] = 'slave_main'
    INPUT_SLAVE_TIMESTAMP: Final[str] = 'slave_timestamp'
    OUTPUT_SYNCHRONIZED_SLAVE: Final[str] = 'synchronized_slave'
    OUTPUT_SYNCHRONIZED_MASTER: Final[str] = 'synchronized_master'
    OUTPUT_SYNCHRONIZED_TIMESTAMP: Final[str] = 'synchronized_timestamp'

    FILL_TYPE_ZEROFILL: Final[str] = 'zero_fill'
    FILL_TYPE_SAMPLE_AND_HOLD: Final[str] = 'sample_and_hold'

    def _validate_parameters(self, parameters: dict):
        parameters['buffer_options']['clear_input_buffer_after_process'] = False
        super()._validate_parameters(parameters)
        if 'slave_filling' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='slave_filling')

        if parameters['slave_filling'] not in [self.FILL_TYPE_ZEROFILL, self.FILL_TYPE_SAMPLE_AND_HOLD]:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='slave_filling',
                                        cause=f'not_in_[{self.FILL_TYPE_ZEROFILL},{self.FILL_TYPE_SAMPLE_AND_HOLD}]')
        if 'statistics_enabled' in parameters and type(parameters['statistics_enabled']) is not bool:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='statistics_enabled',
                                        cause='must_be_bool')

    def _initialize_parameter_fields(self, parameters: dict):
        super()._initialize_parameter_fields(parameters)
        self._statistics_enabled = parameters['statistics_enabled'] if 'statistics_enabled' in parameters else False
        self._zero_fill = parameters['slave_filling'] == self.FILL_TYPE_ZEROFILL
        self._sample_and_hold = parameters['slave_filling'] == self.FILL_TYPE_SAMPLE_AND_HOLD
        self._sync_errors: List[float] = []

    def _is_next_node_call_enabled(self) -> bool:
        return True

    def _is_processing_condition_satisfied(self) -> bool:
        return self._input_buffer[self.INPUT_SLAVE_TIMESTAMP].get_data_count() > 1 \
            and self._input_buffer[self.INPUT_MASTER_TIMESTAMP].get_data_count() > 0 \
            and self._input_buffer[self.INPUT_SLAVE_MAIN].get_data_count() > 0 \
            and self._input_buffer[self.INPUT_MASTER_MAIN].get_data_count() > 0 \
            and (
                    self._input_buffer[self.INPUT_MASTER_TIMESTAMP].get_data_single_channel()[-1]
                    >= self._input_buffer[self.INPUT_SLAVE_TIMESTAMP].get_data_single_channel()[-1]
            )

    def _process(self, input_data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        data = copy.deepcopy(input_data)
        master_timestamp_data = data[self.INPUT_MASTER_TIMESTAMP].get_data_single_channel()
        slave_main = data[self.INPUT_SLAVE_MAIN]
        slave_timestamp = data[self.INPUT_SLAVE_TIMESTAMP]
        slave_timestamp_data = slave_timestamp.get_data_single_channel()

        master_sampling_frequency = data[self.INPUT_MASTER_TIMESTAMP].sampling_frequency
        master_max_index = len(master_timestamp_data) - 1
        master_timestamp_avg_increment = (master_timestamp_data[-1] - master_timestamp_data[0]) / master_max_index

        new_slave_data = FrameworkData(sampling_frequency_hz=master_sampling_frequency,
                                       channels=slave_main.channels)
        max_slave_index = len(slave_timestamp_data) - 1
        last_closest_index = 0
        last_slave_index = 0
        for slave_timestamp_index, slave_timestamp_value in enumerate(slave_timestamp_data):
            # stop processing if slave timestamp is greater than master timestamp, as we can't be sure if there's more master data incoming to sync
            if slave_timestamp_value > master_timestamp_data[master_max_index]:
                break

            # stop processing if it's the last slave timestamp, as we can't be sure if there's more slave data incoming to sync
            if slave_timestamp_index == max_slave_index:
                break

            closest_point_start = self._get_closest_timestamp_index_in_master(
                master_timestamp_data,
                slave_timestamp_value,
                master_timestamp_avg_increment,
                master_max_index
            )
            if last_closest_index == closest_point_start and last_closest_index == 0:
                new_slave_data.splice(0, 1)

            value_index = slave_timestamp_index
            if slave_timestamp_index - 1 >= 0:
                value_index = slave_timestamp_index - 1
            new_slave_data.extend(
                self._fill(
                    last_closest_index,
                    closest_point_start,
                    slave_main,
                    value_index,
                    master_sampling_frequency
                )
            )
            self._statistics(abs(master_timestamp_data[closest_point_start] - slave_timestamp_value) * 1000000)
            last_closest_index = closest_point_start
            last_slave_index = slave_timestamp_index

        self.print(f'------------------------------------------------------------------------------------------------------------------'+
              f'\nOriginal MASTER {master_timestamp_data[0]} - {master_timestamp_data[master_max_index]}'
              f'\nRemoving MASTER {master_timestamp_data[0]} - {master_timestamp_data[last_closest_index]}'
              f'\nOriginal SLAVE  {slave_timestamp_data[0]} - {slave_timestamp_data[max_slave_index]}'
              f'\nRemoving SLAVE  {slave_timestamp_data[0]} - {slave_timestamp_data[last_slave_index]}'
        )

        self._input_buffer[self.INPUT_SLAVE_TIMESTAMP].splice(0, last_slave_index+1)
        self._input_buffer[self.INPUT_SLAVE_MAIN].splice(0, last_slave_index+1)
        output_timestamp = self._input_buffer[self.INPUT_MASTER_TIMESTAMP].splice(0, last_closest_index+1)
        output_master = self._input_buffer[self.INPUT_MASTER_MAIN].splice(0, last_closest_index+1)

        return {
            self.OUTPUT_SYNCHRONIZED_SLAVE: new_slave_data,
            self.OUTPUT_SYNCHRONIZED_MASTER: output_master,
            self.OUTPUT_SYNCHRONIZED_TIMESTAMP: output_timestamp
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
            self.OUTPUT_SYNCHRONIZED_SLAVE,
            self.OUTPUT_SYNCHRONIZED_MASTER,
            self.OUTPUT_SYNCHRONIZED_TIMESTAMP
        ]

    @staticmethod
    def _get_closest_timestamp_index_in_master(
            master_timestamp: List[float],
            slave_timestamp: float,
            master_timestamp_avg_increment: float,
            master_max_index: int) -> int:

        if slave_timestamp < master_timestamp[0]:
            return 0

        estimated_index = int((slave_timestamp - master_timestamp[0]) / master_timestamp_avg_increment)

        if estimated_index < 0:
            return 0

        while 0 < estimated_index < master_max_index - 1:
            if master_timestamp[estimated_index - 1] <= slave_timestamp <= master_timestamp[estimated_index + 1]:
                return estimated_index
            elif slave_timestamp < master_timestamp[estimated_index]:
                estimated_index -= 1
            elif slave_timestamp > master_timestamp[estimated_index]:
                estimated_index += 1

        closest_point: int = min(range(len(master_timestamp)),
                                         key=lambda i: abs(master_timestamp[i] - slave_timestamp))
        return closest_point

    def _fill(self,
              start_index: int,
              end_index: int,
              slave_main: FrameworkData,
              slave_main_value_index: int,
              master_sampling_frequency: float) -> FrameworkData:
        fill_data = FrameworkData(master_sampling_frequency, slave_main.channels)
        fill_size = (end_index - start_index)
        if fill_size > 0:
            if self._zero_fill:
                channel_data = [0] * fill_size
                input_data = slave_main.get_data_at_index(slave_main_value_index)
                for channel in input_data:
                    channel_data = [0] * fill_size
                    channel_data[0] = input_data[channel]
                    fill_data.input_data_on_channel(channel_data, channel)
                input_data = [channel_data] * len(slave_main.channels)
                fill_data.input_2d_data(input_data)
            elif self._sample_and_hold:
                input_data = slave_main.get_data_at_index(slave_main_value_index)
                for channel in input_data:
                    channel_data = [input_data[channel]] * fill_size
                    fill_data.input_data_on_channel(channel_data, channel)
            else:
                raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                            parameter='slave_filling',
                                            cause='not_set')
        if fill_data.get_data_count() == 0 and start_index == end_index:
            for channel in fill_data.channels:
                fill_data.input_data_on_channel([slave_main.get_data_on_channel(channel)[0]], channel)
        return fill_data
