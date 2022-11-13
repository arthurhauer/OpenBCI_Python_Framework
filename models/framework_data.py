from __future__ import annotations
from typing import Final, List, Dict

from models.exception.non_compatible_data import NonCompatibleData


class FrameworkData:
    _MODULE_NAME: Final[str] = 'models'
    _DEFAULT_CHANNEL_NAME: Final[str] = 'main'

    def __init__(self, channels: List[str] = None):
        if channels is None:
            self.channels = []
        else:
            self.channels = channels
        self._init_data_dictionary()

    @classmethod
    def from_single_channel(cls, data: list):
        class_data = cls(
            [cls._DEFAULT_CHANNEL_NAME]
        )
        class_data.input_data_on_channel(cls._DEFAULT_CHANNEL_NAME, data)
        return class_data

    @classmethod
    def from_multi_channel(cls, channels: List[str], data: List[list]):
        class_data = cls(
            channels
        )
        class_data.input_2d_data(data)
        return class_data

    def _init_data_dictionary(self):
        self._data: Dict[str, List[float]] = dict.fromkeys(self.channels, [])

    def extend(self, data: FrameworkData):
        if len(self.channels) == 0:
            self.channels = data.channels

        for channel in self.channels:
            try:
                self._data[channel] = data.get_data(channel)
            except KeyError:
                raise NonCompatibleData(module=self._MODULE_NAME)

    def input_2d_data(self, data: List[list]):
        self_data_len = len(self._data)
        input_data_len = len(data)
        if self_data_len == 0:
            raise NonCompatibleData(module=self._MODULE_NAME)
        if self_data_len != input_data_len:
            raise NonCompatibleData(module=self._MODULE_NAME)

        for index, channel in enumerate(self._data):
            self.input_data_on_channel(channel, data[index])

    def input_data_on_channel(self, channel: str, data: list):
        if len(self._data[channel]) == 0:
            self._data[channel] = []
        self._data[channel].extend(data)

    def get_data(self, channel: str) -> list:
        return self._data[channel]

    def get_data_as_2d_array(self) -> List[list]:
        return_value = []
        for channel in self.channels:
            return_value.append(self._data[channel])
        return return_value

    def has_data(self) -> bool:
        return len(self._data) > 0 and len(self._data[self.channels[0]]) > 0
