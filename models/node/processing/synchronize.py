import statistics
import copy
from bisect import bisect_left
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
        parameters['buffer_options']['clear_input_buffer_after_process'] = True
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
        self._exec_index = 0
        self._last_valid_data = None
        self._initialize_sync_buffer()

    def _is_next_node_call_enabled(self) -> bool:
        return True

    def _initialize_sync_buffer(self):
        """Sets sync buffer to new empty object for each input name
        """
        self._sync_buffer = {}
        for input_name in self._get_inputs():
            self._sync_buffer[input_name] = FrameworkData()

    def _insert_data_in_sync_buffer(self, data: Dict[str, FrameworkData]):
        input_data = copy.deepcopy(data)
        for input_name in self._get_inputs():
            self._sync_buffer[input_name].extend(input_data[input_name])

    def _check_for_timestamp_intersection(self, slave_timestamp_data: List[float],
                                          master_timestamp_data: List[float]) -> bool:
        slave_start = slave_timestamp_data[0]
        slave_end = slave_timestamp_data[-1]
        master_start = master_timestamp_data[0]
        master_end = master_timestamp_data[-1]
        return slave_start < master_end and slave_end > master_start

    def _move_input_buffer_to_sync_buffer(self):
        slave_main_length = self._input_buffer[self.INPUT_SLAVE_MAIN].get_data_count()
        slave_timestamp_length = self._input_buffer[self.INPUT_SLAVE_TIMESTAMP].get_data_count()
        master_main_length = self._input_buffer[self.INPUT_MASTER_MAIN].get_data_count()
        master_timestamp_length = self._input_buffer[self.INPUT_MASTER_TIMESTAMP].get_data_count()
        slave_main = self._input_buffer[self.INPUT_SLAVE_MAIN]
        slave_timestamp = self._input_buffer[self.INPUT_SLAVE_TIMESTAMP]
        master_main = self._input_buffer[self.INPUT_MASTER_MAIN]
        master_timestamp = self._input_buffer[self.INPUT_MASTER_TIMESTAMP]
        self._sync_buffer[self.INPUT_SLAVE_MAIN].extend(slave_main.splice(0, min(slave_main_length, slave_timestamp_length)))
        self._sync_buffer[self.INPUT_SLAVE_TIMESTAMP].extend(slave_timestamp.splice(0, min(slave_main_length, slave_timestamp_length)))
        self._sync_buffer[self.INPUT_MASTER_MAIN].extend(master_main.splice(0, min(master_main_length, master_timestamp_length)))
        self._sync_buffer[self.INPUT_MASTER_TIMESTAMP].extend(master_timestamp.splice(0, min(master_main_length, master_timestamp_length)))

    def _process_input_buffer(self):
        self._move_input_buffer_to_sync_buffer()

        if not self._is_processing_condition_satisfied():
            return

        processed_data = self._process(copy.deepcopy(self._sync_buffer))

        if self._clear_output_buffer_after_process:
            self._clear_output_buffer()
        self.print('Outputting data')
        for output_name in self._get_outputs():
            self._insert_new_output_data(processed_data[output_name], output_name)

    def _is_processing_condition_satisfied(self) -> bool:
        input_data = self._sync_buffer
        slave_timestamp = input_data[self.INPUT_SLAVE_TIMESTAMP]
        master_timestamp = input_data[self.INPUT_MASTER_TIMESTAMP]
        slave_main = input_data[self.INPUT_SLAVE_MAIN]
        master_main = input_data[self.INPUT_MASTER_MAIN]

        return (slave_timestamp.get_data_count() > 2
                     and master_timestamp.get_data_count() > 2
                     and slave_main.get_data_count() == slave_timestamp.get_data_count()
                     and master_main.get_data_count() == master_timestamp.get_data_count()
                     and self._check_for_timestamp_intersection(slave_timestamp.get_data_single_channel(), master_timestamp.get_data_single_channel()))

    def _process(self, input_data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        self._exec_index += 1
        if self._exec_index == 1:
            input_data = self._trim_start(input_data)
        input_data = self._trim_end(input_data)
        master_timestamp_data = input_data[self.INPUT_MASTER_TIMESTAMP].get_data_single_channel()
        slave_main = input_data[self.INPUT_SLAVE_MAIN]
        slave_timestamp = input_data[self.INPUT_SLAVE_TIMESTAMP]
        slave_timestamp_data = slave_timestamp.get_data_single_channel()

        if slave_timestamp.get_data_count() < 1 or len(master_timestamp_data) < 1:
            return {
                self.OUTPUT_SYNCHRONIZED_SLAVE: slave_main,
                self.OUTPUT_SYNCHRONIZED_MASTER: input_data[self.INPUT_MASTER_MAIN],
                self.OUTPUT_SYNCHRONIZED_TIMESTAMP: input_data[self.INPUT_MASTER_TIMESTAMP]
            }

        filled_slave_data = self._fill(master_timestamp_data, slave_timestamp_data, slave_main,
                                       input_data[self.INPUT_MASTER_TIMESTAMP].sampling_frequency)

        return {
            self.OUTPUT_SYNCHRONIZED_SLAVE: filled_slave_data,
            self.OUTPUT_SYNCHRONIZED_MASTER: input_data[self.INPUT_MASTER_MAIN],
            self.OUTPUT_SYNCHRONIZED_TIMESTAMP: input_data[self.INPUT_MASTER_TIMESTAMP]
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

    def _get_closest_timestamp_index_in_master(
            self,
            master_timestamp: List[float],
            slave_timestamp: float,
            master_timestamp_avg_increment: float,
            master_max_index: int) -> int:

        if slave_timestamp < master_timestamp[0]:
            return 0

        estimated_index = int((slave_timestamp - master_timestamp[0]) / master_timestamp_avg_increment)
        bisect_index = bisect_left(master_timestamp, slave_timestamp)
        if estimated_index < 0:
            return 0

        if estimated_index < 0 and slave_timestamp <= master_timestamp[0]:
            return 0
        elif estimated_index > master_max_index and slave_timestamp >= master_timestamp[master_max_index]:
            return master_max_index
        elif estimated_index == 0 and slave_timestamp < master_timestamp[1]:
            return estimated_index
        elif estimated_index == master_max_index and (slave_timestamp > master_timestamp[master_max_index - 1]):
            return estimated_index

        while 0 < estimated_index < master_max_index:
            if master_timestamp[estimated_index - 1] <= slave_timestamp <= master_timestamp[estimated_index + 1]:
                return estimated_index
            elif slave_timestamp < master_timestamp[estimated_index]:
                estimated_index -= 1
            elif slave_timestamp > master_timestamp[estimated_index]:
                estimated_index += 1

        closest_point: int = min(range(len(master_timestamp)),
                                 key=lambda i: abs(master_timestamp[i] - slave_timestamp))
        return closest_point

    def _trim_start(self, input_data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        index = 0
        slave_timestamp = input_data[self.INPUT_SLAVE_TIMESTAMP]
        slave_main = input_data[self.INPUT_SLAVE_MAIN]
        master_timestamp = input_data[self.INPUT_MASTER_TIMESTAMP]
        master_main = input_data[self.INPUT_MASTER_MAIN]
        slave_timestamp_data = slave_timestamp.get_data_single_channel()
        master_timestamp_data = master_timestamp.get_data_single_channel()

        slave_avg_increment = (slave_timestamp_data[-1] - slave_timestamp_data[0]) / len(slave_timestamp_data)
        master_avg_increment = (master_timestamp_data[-1] - master_timestamp_data[0]) / len(master_timestamp_data)

        should_trim_slave = slave_timestamp_data[index] < master_timestamp_data[index]
        should_trim_master = master_timestamp_data[index] < slave_timestamp_data[index]

        if should_trim_slave:
            slave_index = self._get_closest_timestamp_index_in_master(
                slave_timestamp_data,
                master_timestamp_data[index],
                slave_avg_increment,
                len(slave_timestamp_data) - 1
            )
            start_index = 0
            remove_count = slave_index
            slave_timestamp.splice(start_index, remove_count)
            slave_main.splice(start_index, remove_count)
            self._sync_buffer[self.INPUT_SLAVE_TIMESTAMP].splice(0, slave_index)
            self._sync_buffer[self.INPUT_SLAVE_MAIN].splice(0, slave_index)

        elif should_trim_master:
            master_index = self._get_closest_timestamp_index_in_master(
                master_timestamp_data,
                slave_timestamp_data[index],
                master_avg_increment,
                len(master_timestamp_data) - 1
            )
            start_index = 0
            remove_count = master_index
            master_timestamp.splice(start_index, remove_count)
            master_main.splice(start_index, remove_count)
            self._sync_buffer[self.INPUT_MASTER_TIMESTAMP].splice(0, master_index)
            self._sync_buffer[self.INPUT_MASTER_MAIN].splice(0, master_index)

        return {
            self.INPUT_MASTER_MAIN: master_main,
            self.INPUT_MASTER_TIMESTAMP: master_timestamp,
            self.INPUT_SLAVE_MAIN: slave_main,
            self.INPUT_SLAVE_TIMESTAMP: slave_timestamp
        }

    def _trim_end(self, input_data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        index = -1
        slave_timestamp = input_data[self.INPUT_SLAVE_TIMESTAMP]
        slave_main = input_data[self.INPUT_SLAVE_MAIN]
        master_timestamp = input_data[self.INPUT_MASTER_TIMESTAMP]
        master_main = input_data[self.INPUT_MASTER_MAIN]
        slave_timestamp_data = slave_timestamp.get_data_single_channel()
        master_timestamp_data = master_timestamp.get_data_single_channel()
        slave_avg_increment = (slave_timestamp_data[-1] - slave_timestamp_data[0]) / len(slave_timestamp_data)
        master_avg_increment = (master_timestamp_data[-1] - master_timestamp_data[0]) / len(master_timestamp_data)

        should_trim_slave = slave_timestamp_data[index] > master_timestamp_data[index]
        should_trim_master = master_timestamp_data[index] > slave_timestamp_data[index]

        if should_trim_slave:
            while int((slave_timestamp_data[index] - master_timestamp_data[0]) / master_avg_increment) > len(
                    master_timestamp_data) - 1:
                index -= 1
                if index < -len(slave_timestamp_data):
                    return {
                        self.INPUT_MASTER_MAIN: FrameworkData(sampling_frequency_hz=master_main.sampling_frequency,
                                                              channels=master_main.channels),
                        self.INPUT_MASTER_TIMESTAMP: FrameworkData(
                            sampling_frequency_hz=master_timestamp.sampling_frequency,
                            channels=master_timestamp.channels),
                        self.INPUT_SLAVE_MAIN: FrameworkData(sampling_frequency_hz=slave_main.sampling_frequency,
                                                             channels=slave_main.channels),
                        self.INPUT_SLAVE_TIMESTAMP: FrameworkData(
                            sampling_frequency_hz=slave_timestamp.sampling_frequency, channels=slave_timestamp.channels)
                    }
            master_index = self._get_closest_timestamp_index_in_master(
                master_timestamp_data,
                slave_timestamp_data[index],
                master_avg_increment,
                len(master_timestamp_data) - 1
            )
            # keep slave data from index to end in sync buffer and remove the rest
            self._sync_buffer[self.INPUT_SLAVE_TIMESTAMP].splice(0, len(slave_timestamp_data) + index + 1)
            self._sync_buffer[self.INPUT_SLAVE_MAIN].splice(0, len(slave_timestamp_data) + index + 1)
            # process slave data from 0 to index
            slave_main.splice(len(slave_timestamp_data) + index + 1, -index)
            slave_timestamp.splice(len(slave_timestamp_data) + index + 1, -index)
            # keep master data from master_index to end in sync buffer and remove the rest
            self._sync_buffer[self.INPUT_MASTER_TIMESTAMP].splice(0, master_index + 1)
            self._sync_buffer[self.INPUT_MASTER_MAIN].splice(0, master_index + 1)
            # process master data from 0 to master_index
            master_main.splice(master_index + 1, len(master_timestamp_data) - master_index)
            master_timestamp.splice(master_index + 1, len(master_timestamp_data) - master_index)

        elif should_trim_master:
            while int((master_timestamp_data[index] - slave_timestamp_data[0]) / slave_avg_increment) > len(
                    slave_timestamp_data) - 1:
                index -= 1
                if index < -len(master_timestamp_data):
                    # return empty data
                    return {
                        self.INPUT_MASTER_MAIN: FrameworkData(sampling_frequency_hz=master_main.sampling_frequency,
                                                              channels=master_main.channels),
                        self.INPUT_MASTER_TIMESTAMP: FrameworkData(
                            sampling_frequency_hz=master_timestamp.sampling_frequency,
                            channels=master_timestamp.channels),
                        self.INPUT_SLAVE_MAIN: FrameworkData(sampling_frequency_hz=slave_main.sampling_frequency,
                                                             channels=slave_main.channels),
                        self.INPUT_SLAVE_TIMESTAMP: FrameworkData(
                            sampling_frequency_hz=slave_timestamp.sampling_frequency, channels=slave_timestamp.channels)
                    }

            slave_index = self._get_closest_timestamp_index_in_master(
                slave_timestamp_data,
                master_timestamp_data[index],
                slave_avg_increment,
                len(slave_timestamp_data) - 1
            )
            # keep master data from index to end in sync buffer and remove the rest
            self._sync_buffer[self.INPUT_MASTER_TIMESTAMP].splice(0, len(master_timestamp_data) + index + 1)
            self._sync_buffer[self.INPUT_MASTER_MAIN].splice(0, len(master_timestamp_data) + index + 1)
            # process master data from 0 to index
            master_main.splice(len(master_timestamp_data) + index + 1, -index)
            master_timestamp.splice(len(master_timestamp_data) + index + 1, -index)
            # keep slave data from slave_index to end in sync buffer and remove the rest
            self._sync_buffer[self.INPUT_SLAVE_TIMESTAMP].splice(0, slave_index + 1)
            self._sync_buffer[self.INPUT_SLAVE_MAIN].splice(0, slave_index + 1)
            # process slave data from 0 to slave_index
            slave_main.splice(slave_index + 1, len(master_timestamp_data) - slave_index)
            slave_timestamp.splice(slave_index + 1, len(master_timestamp_data) - slave_index)

        return {
            self.INPUT_MASTER_MAIN: master_main,
            self.INPUT_MASTER_TIMESTAMP: master_timestamp,
            self.INPUT_SLAVE_MAIN: slave_main,
            self.INPUT_SLAVE_TIMESTAMP: slave_timestamp
        }

    def _fill(self, master_timestamp: List[float], slave_timestamp: List[float],
              slave_main: FrameworkData, master_sampling_frequency: float) -> FrameworkData:
        """Fills slave data to align with master timestamps using sample-and-hold."""

        # Create FrameworkData to store filled data
        fill_data = FrameworkData(master_sampling_frequency, slave_main.channels)

        # Calculate average increment between master timestamps
        max_slave_index = len(slave_timestamp) - 1
        max_master_index = len(master_timestamp) - 1
        previous_master_index = -1  # Start before the first index
        # Iterate over slave timestamps
        for current_slave_index, slave_time in enumerate(slave_timestamp):

            # Ignore repeated slave timestamps
            if current_slave_index > 0 and slave_time == slave_timestamp[current_slave_index - 1]:
                continue

            # Use binary search to find the closest master timestamp index
            master_index = bisect_left(master_timestamp, slave_time)

            # Ensure master_index does not exceed valid range
            if master_index > max_master_index:
                master_index = max_master_index

            # Calculate how many master timestamps need to be filled
            fill_size = master_index - previous_master_index - 1

            # If there's a gap, fill it using the last valid data or 0
            if fill_size > 0 and self._last_valid_data is not None:
                for channel in slave_main.channels:
                    fill_content = [self._last_valid_data[channel]] * fill_size if self._sample_and_hold else [
                                                                                                                  0] * fill_size
                    fill_data.input_data_on_channel(fill_content, channel)

            # If aligning slave data, or it's the first valid data point
            if (
                    self._last_valid_data is None or master_index >= previous_master_index) and current_slave_index <= max_slave_index:
                # Update last valid data with current slave data
                self._last_valid_data = slave_main.get_data_at_index(current_slave_index)

                # Store slave data for all channels at the aligned master timestamp
                for channel in slave_main.channels:
                    fill_data.input_data_on_channel([self._last_valid_data[channel]], channel)

            # Update the previous master index for the next iteration
            previous_master_index = master_index

        # Fill any remaining master timestamps with sample-and-hold or 0
        remaining_fill_size = max_master_index - previous_master_index
        if remaining_fill_size > 0 and self._last_valid_data is not None:
            for channel in slave_main.channels:
                fill_content = [self._last_valid_data[channel]] * remaining_fill_size if self._sample_and_hold else [
                                                                                                                        0] * remaining_fill_size
                fill_data.input_data_on_channel(fill_content, channel)

        return fill_data
