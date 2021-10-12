import numpy
from nptyping import NDArray, Float

from board_communication.models.accelerometer_data import AccelerometerData


class BoardData:

    def __init__(self):
        super(BoardData, self).__init__()
        self._eeg_data = None
        self._accelerometer_data = AccelerometerData()

    def get_eeg_data(self) -> NDArray[Float]:
        return self._eeg_data

    def get_accelerometer_data(self) -> AccelerometerData:
        return self._accelerometer_data

    def append_eeg_data(self, data: NDArray[Float]):
        if self._eeg_data is None:
            self._eeg_data = data
            return
        self._eeg_data = numpy.concatenate((self._eeg_data, data), axis=1)

    def append_accelerometer_data(self, data: NDArray[Float]):
        self._accelerometer_data.append_data(data)

    def append_data(self, data: NDArray[Float], eeg_channels: list, accelerometer_channels: list):
        self.append_eeg_data(data[eeg_channels])
        self.append_accelerometer_data(data[accelerometer_channels])
