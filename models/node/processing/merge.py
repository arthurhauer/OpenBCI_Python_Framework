import abc
import string
from random import random
from typing import List, Dict, Final
from models.framework_data import FrameworkData
from models.node.processing.synchronize import Synchronize


class Merge(Synchronize):
    _MODULE_NAME: Final[str] = 'node.processing.merge'

    OUTPUT_MERGED_MAIN: Final[str] = 'merged_main'
    OUTPUT_MERGED_TIMESTAMP: Final[str] = 'merged_timestamp'

    @abc.abstractmethod
    def _validate_parameters(self, parameters: dict):
        super()._validate_parameters(parameters)

    @abc.abstractmethod
    def _initialize_parameter_fields(self, parameters: dict):
        super()._initialize_parameter_fields(parameters)

    def _is_next_node_call_enabled(self) -> bool:
        return self._output_buffer[self.OUTPUT_MERGED_MAIN].get_data_count() > 0

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        synchronized_data: Dict[str, FrameworkData] = super()._process(data)
        new_slave_data = synchronized_data[self.OUTPUT_SYNCHRONIZED_MAIN]
        master_main = data[self.INPUT_MASTER_MAIN]
        if new_slave_data.get_data_count() < master_main.get_data_count():
            new_slave_data.extend(
                super()._fill(new_slave_data.get_data_count() - 1, master_main.get_data_count() - 1, new_slave_data,
                              new_slave_data.get_data_count() - 1, new_slave_data.sampling_frequency)
            )
        merged_data = FrameworkData()
        merged_data.extend(master_main)
        for channel in new_slave_data.channels:
            new_channel_name = channel
            if channel in merged_data.channels:
                rand_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                new_channel_name = f'{channel}{rand_id}'
            merged_data.input_data_on_channel(new_slave_data.get_data_on_channel(channel), new_channel_name)
        return {
            self.OUTPUT_MERGED_MAIN: merged_data,
            self.OUTPUT_MERGED_TIMESTAMP: data[self.INPUT_MASTER_TIMESTAMP]
        }

    def _get_outputs(self) -> List[str]:
        return [
            self.OUTPUT_MERGED_MAIN,
            self.OUTPUT_MERGED_TIMESTAMP
        ]
