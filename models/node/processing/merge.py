import statistics
from typing import List, Dict, Final

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode


# TODO implementar
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

        self._zero_fill = parameters['slave_filling'] == self.FILL_TYPE_ZEROFILL
        self._sample_and_hold = parameters['slave_filling'] == self.FILL_TYPE_SAMPLE_AND_HOLD

    @classmethod
    def from_config_json(cls, parameters: dict):
        return cls(parameters)

    def _is_next_node_call_enabled(self) -> bool:
        return True

    def _is_processing_condition_satisfied(self) -> bool:
        return len(self._input_buffer[self.INPUT_SLAVE_TIMESTAMP]) > 0 \
               and len(self._input_buffer[self.INPUT_MASTER_TIMESTAMP]) > 0 \
               and (
                       self._input_buffer[self.INPUT_MASTER_TIMESTAMP][-1]
                       >= self._input_buffer[self.INPUT_SLAVE_TIMESTAMP][-1]
               )

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        lookup_start_index = 0

        master_main = data[self.INPUT_MASTER_MAIN]
        master_timestamp = data[self.INPUT_MASTER_TIMESTAMP]
        slave_main = data[self.INPUT_SLAVE_MAIN]
        slave_timestamp = data[self.INPUT_SLAVE_TIMESTAMP]
        new_slave_data = []

        for slave_timestamp_index, slave_timestamp_value in enumerate(slave_timestamp):
            closest_point = self._get_closest_timestamp_index_in_master(
                master_timestamp,
                slave_timestamp_value,
                lookup_start_index
            )
            new_slave_data.extend(
                self._fill(
                    lookup_start_index,
                    closest_point,
                    slave_main[slave_timestamp_index]
                )
            )
            self._statistics(abs(master_timestamp[closest_point] - slave_timestamp_value) * 1000000)

            lookup_start_index = closest_point

        merged_data = master_main
        merged_data.extend(new_slave_data)
        return {
            self.OUTPUT_MERGED_MAIN: merged_data,
            self.OUTPUT_MERGED_TIMESTAMP: data[self.INPUT_MASTER_TIMESTAMP]
        }

    def _statistics(self, sync_error_microseconds: float):
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

    def _fill(self, start_index: int, end_index: int, slave_main_value: FrameworkData) -> FrameworkData:
        # TODO Tratar caso slave multi-canal
        fill_data = None

        if self._zero_fill:
            fill_data = 0
        elif self._sample_and_hold:
            fill_data = slave_main_value
        else:
            raise InvalidParameterValue(module=self._MODULE_NAME,
                                        parameter='slave_filling',
                                        cause='not_set')

        return [fill_data] * (end_index - start_index)
