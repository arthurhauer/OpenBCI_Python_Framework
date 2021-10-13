import numpy
from nptyping import NDArray, Float


class AccelerometerData:
    def __init__(self, data: NDArray[Float] = None) -> None:
        super().__init__()
        self._x = None
        self._y = None
        self._z = None
        if data is not None:
            self.append_raw_data(data)

    def append_raw_data(self, data: NDArray[Float]):
        self.append_x_axis(data[0][:])
        self.append_y_axis(data[1][:])
        self.append_z_axis(data[2][:])

    def append_data(self,data):
        self.append_x_axis(data.get_x_axis())
        self.append_y_axis(data.get_y_axis())
        self.append_z_axis(data.get_z_axis())

    def append_x_axis(self, data: NDArray[Float]):
        if self._x is None:
            self._x = data
            return
        self._x = numpy.concatenate((self._x, data), axis=0)

    def append_y_axis(self, data: NDArray[Float]):
        if self._y is None:
            self._y = data
            return
        self._y = numpy.concatenate((self._y, data), axis=0)

    def append_z_axis(self, data: NDArray[Float]):
        if self._z is None:
            self._z = data
            return
        self._z = numpy.concatenate((self._z, data), axis=0)

    def get_x_axis(self) -> NDArray[Float]:
        return self._x

    def get_y_axis(self) -> NDArray[Float]:
        return self._y

    def get_z_axis(self) -> NDArray[Float]:
        return self._z

    def as_array(self) -> NDArray[Float]:
        return numpy.array([self.get_x_axis(), self.get_y_axis(), self.get_z_axis()])
