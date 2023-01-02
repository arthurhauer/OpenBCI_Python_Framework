from __future__ import annotations
from typing import Final, List, Dict

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.exception.non_compatible_data import NonCompatibleData


class FrameworkData:
    _MODULE_NAME: Final[str] = 'models.framework_data'
    _DEFAULT_CHANNEL_NAME: Final[str] = 'main'

    def __init__(self, sampling_frequency_hz: float = None, channels: List[str] = None, ):
        if channels is None:
            self._channels_set = None
            self.channels = []
        else:
            self.channels = channels
            self._channels_set = set(self.channels)
        self._init_data_dictionary()
        self.sampling_frequency = sampling_frequency_hz

    @classmethod
    def from_single_channel(cls, sampling_frequency_hz: float, data: list):
        class_data = cls(
            sampling_frequency_hz,
            [cls._DEFAULT_CHANNEL_NAME]
        )
        class_data.input_data_on_channel(cls._DEFAULT_CHANNEL_NAME, data)
        return class_data

    @classmethod
    def from_multi_channel(cls, sampling_frequency_hz: float, channels: List[str], data: List[list]):
        class_data = cls(
            sampling_frequency_hz,
            channels
        )
        class_data.input_2d_data(data)
        return class_data

    def _init_data_dictionary(self):
        self._data = {}
        for channel in self.channels:
            self._data[channel] = []

    def get_data_count(self):
        if len(self.channels) == 0:
            return 0
        return len(self._data[self.channels[0]])

    def get_channels_as_set(self):
        if self._channels_set is None:
            self._channels_set = set(self.channels)
        return self._channels_set

    def extend(self, data: FrameworkData):
        if len(self.channels) == 0:
            self.channels = data.channels
            self.sampling_frequency = data.sampling_frequency
            self._init_data_dictionary()

        elif self.sampling_frequency != data.sampling_frequency:
            raise NonCompatibleData(module=self._MODULE_NAME)
        elif self.get_channels_as_set() != data.get_channels_as_set():
            raise NonCompatibleData(module=self._MODULE_NAME)

        for channel in self.channels:
            try:
                self._data[channel].extend(data.get_data(channel))
            except KeyError:
                raise NonCompatibleData(module=self._MODULE_NAME)

    # def input_dict_data(self,data:dict):
    #

    def input_2d_data(self, data: List[list]):
        self_data_len = len(self._data)
        input_data_len = len(data)
        if self_data_len == 0:
            raise NonCompatibleData(module=self._MODULE_NAME)
        if self_data_len != input_data_len:
            raise NonCompatibleData(module=self._MODULE_NAME)

        for index, channel in enumerate(self._data):
            self.input_data_on_channel(channel, data[index])

    def input_data_on_channel(self, channel: str = None, data: list = []):
        if channel is None:
            if len(self.channels) < 1:
                self.channels.append(self._DEFAULT_CHANNEL_NAME)
            channel = self.channels[0]
        if channel not in self._data:
            self._data[channel] = []
            self.channels.append(channel)
            self._channels_set = None
        self._data[channel].extend(data)

    def get_data_single_channel(self) -> list:
        if not len(self._data) == 1:
            raise NonCompatibleData(module=self._MODULE_NAME, cause='operation_allowed_on_single_channel_only')
        return self._data[self.channels[0]]

    def get_data(self, channel: str) -> list:
        return self._data[channel]

    def get_data_as_2d_array(self) -> List[list]:
        return_value = []
        for channel in self.channels:
            return_value.append(self._data[channel])
        return return_value

    def get_data_at_index(self, index: int) -> Dict[str, list]:
        return_value = {}
        for channel in self.channels:
            return_value[channel] = self._data[channel][index]
        return return_value

    def has_data(self) -> bool:
        return len(self._data) > 0 and len(self._data[self.channels[0]]) > 0
