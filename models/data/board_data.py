from typing import List

import numpy
from nptyping import NDArray, Float

from models.data.accelerometer_data import AccelerometerData


class BoardData:

    def __init__(self, eeg_channels: List[str], timestamp: NDArray[Float] = None, eeg: NDArray[Float] = None,
                 accelerometer: NDArray[Float] = None):
        super(BoardData, self).__init__()
        self._eeg_channels = eeg_channels
        self._timestamp = timestamp
        self._eeg_data = eeg
        self._accelerometer_data = AccelerometerData(accelerometer)

    def get_eeg_channels(self) -> List[str]:
        return self._eeg_channels

    def get_timestamp(self) -> NDArray[Float]:
        return self._timestamp

    def get_eeg_data(self) -> NDArray[Float]:
        return self._eeg_data

    def get_accelerometer_data(self) -> AccelerometerData:
        return self._accelerometer_data

    def append_timestamp(self, data: NDArray[Float]):
        if self._timestamp is None:
            self._timestamp = data
            return
        self._timestamp = numpy.concatenate((self._timestamp, data))

    def append_eeg_data(self, data: NDArray[Float]):
        if self._eeg_data is None:
            self._eeg_data = data
            return
        self._eeg_data = numpy.concatenate((self._eeg_data, data), axis=1)

    def append_accelerometer_data(self, data: NDArray[Float]):
        self._accelerometer_data.append_data(data)

    def append_new_data(self, new_data):
        self.append_timestamp(new_data.get_timestamp())
        self.append_eeg_data(new_data.get_eeg_data())
        self._accelerometer_data.append_data(new_data.get_accelerometer_data())

    def append_data(self, data: NDArray[Float], eeg_channels: list, accelerometer_channels: list,
                    timestamp_channel: int):
        self.append_timestamp(data[timestamp_channel])
        self.append_eeg_data(data[eeg_channels])
        self.append_accelerometer_data(data[accelerometer_channels])
