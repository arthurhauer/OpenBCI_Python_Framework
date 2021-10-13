from typing import List
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui

from models.data.board_data import BoardData
from config.configuration import Configuration


class Graph:
    def __init__(self, sampling_rate: int, eeg_channels: List[str]) -> None:
        super().__init__()
        self.eeg_channels = eeg_channels
        self.eeg_channels.append('x')
        self.eeg_channels.append('y')
        self.eeg_channels.append('z')
        self.window_size = Configuration.get_graphing_window_size()
        self.sampling_rate = sampling_rate
        self.num_points = self.window_size * self.sampling_rate
        self.app = QtGui.QApplication([])
        self.win = pg.GraphicsWindow(title='BrainFlow Plot', size=(800, 600))
        self._init_timeseries()

    def _init_timeseries(self):
        self.plots = list()
        self.curves = list()
        for i in range(len(self.eeg_channels)):
            p = self.win.addPlot(row=i, col=0)
            p.showAxis('left', False)
            p.setMenuEnabled('left', False)
            p.showAxis('bottom', False)
            p.setMenuEnabled('bottom', False)
            p.setTitle(self.eeg_channels[i])
            self.plots.append(p)
            curve = p.plot()
            self.curves.append(curve)

    def plot_data(self, data: BoardData):
        for count in range(len(self.eeg_channels)-3):
            self.curves[count].setData(data.get_eeg_data()[count].tolist())
        self.curves[8].setData(data.get_accelerometer_data().get_x_axis())
        self.curves[9].setData(data.get_accelerometer_data().get_y_axis())
        self.curves[10].setData(data.get_accelerometer_data().get_z_axis())
        self.app.processEvents()
