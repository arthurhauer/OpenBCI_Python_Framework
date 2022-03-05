from typing import List

import pyqtgraph as pg
from nptyping import Float
from numpy.typing import NDArray
from pyqtgraph.Qt import QtGui

from config.configuration import Configuration
from models.data.channel import Channel


class Graph:
    def __init__(self, sampling_rate: int, channels: List[Channel]) -> None:
        super().__init__()
        self.channels = channels
        self.window_size = Configuration.get_graphing_window_size()
        self.sampling_rate = sampling_rate
        self.num_points = self.window_size * self.sampling_rate
        self.app = QtGui.QApplication([])
        self.win = pg.GraphicsWindow(title='BrainFlow Plot', size=(800, 600))
        self._init_timeseries()

    def _init_timeseries(self):
        self.plots = list()
        self.curves = list()
        for i, channel in enumerate(self.channels):
            if channel.show:
                p = self.win.addPlot(row=i, col=0)
                p.showAxis('left', False)
                p.setMenuEnabled('left', False)
                p.showAxis('bottom', False)
                p.setMenuEnabled('bottom', False)
                p.setTitle(channel.name)
                self.plots.append(p)
                curve = p.plot()
                self.curves.append(curve)

    def plot_data(self, data: NDArray[Float]):
        for i in range(len(self.channels)):
            data_len = len(data[i])
            if data_len <= self.window_size:
                windowed_data = data[i]
            else:
                windowed_data = data[i][data_len - self.window_size - 1:data_len - 1]
            self.curves[i].setData(windowed_data)
        self.app.processEvents()
