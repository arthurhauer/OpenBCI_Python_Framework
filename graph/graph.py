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
        self.samples = Configuration.get_graphing_plot_samples()
        self.app = QtGui.QApplication([])
        self.win = pg.GraphicsWindow(title='BrainFlow Plot',
                                     size=(self.window_size["width"], self.window_size["height"]))
        self._init_timeseries()

    def _init_timeseries(self):
        self.plots = list()
        self.curves = list()
        self.channel_curve_map = {}
        curve_index = 0
        for i, channel in enumerate(self.channels):
            if channel.show:
                self.channel_curve_map[i] = curve_index
                p = self.win.addPlot(row=i, col=0)
                p.showAxis('left', False)
                p.setMenuEnabled('left', False)
                p.showAxis('bottom', False)
                p.setMenuEnabled('bottom', False)
                p.setTitle(channel.name)
                self.plots.append(p)
                curve = p.plot()
                self.curves.append(curve)
                curve_index += 1

    def plot_data(self, data: NDArray[Float]):
        data_len = len(data)
        for i in range(len(self.channels)):
            if i in self.channel_curve_map.keys() and i < data_len:
                signal_len = len(data[i])
                if signal_len <= self.samples:
                    windowed_data = data[i]
                else:
                    windowed_data = data[i][signal_len - self.samples - 1:signal_len - 1]
                self.curves[self.channel_curve_map[i]].setData(windowed_data)
        self.app.processEvents()
