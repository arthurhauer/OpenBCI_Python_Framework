from threading import Thread

import numpy
from nptyping import Float
from numpy.typing import NDArray

from config.configuration import Configuration
from models.data.board_data import BoardData
from board_communication.open_bci_board import OpenBCIBoard
from graph.graph import Graph
from pyqtgraph.Qt import QtGui

from models.data.channel import Channel
from models.preprocessing.custom import Custom
from models.preprocessing.denoise import Denoise
from models.preprocessing.detrend import Detrend
from models.preprocessing.downsample import Downsample
from models.preprocessing.filter.band_filter import BandFilter
from models.preprocessing.filter.cutoff_filter import CutOffFilter
from models.preprocessing.signal_check import SignalCheck
from models.preprocessing.smooth import Smooth
from preprocessing.preprocessing import PreProcessing


class Application:

    def __init__(self, board: OpenBCIBoard = OpenBCIBoard.from_config_json()) -> None:
        super().__init__()
        self.board = board
        # self.data = BoardData(self.board.get_eeg_channel_names())
        self.data = None
        channels = []
        for channel in Configuration.get_channel_mapping():
            channels.append(Channel.from_config_json(channel))
        if len(channels) == 0:
            for channel in board.get_eeg_channel_names():
                channels.append(Channel(channel))
        self.graph = Graph(self.board.get_sampling_rate(), channels)
        # self.gui_thread =
        self.start()
        import time
        time.sleep(60)
        self.stop()

    @classmethod
    def as_sdk(cls):
        preprocessing: PreProcessing = PreProcessing()
        from brainflow import DataFilter
        board = OpenBCIBoard(
            log_level="INFO",
            board="SYNTHETIC_BOARD",
            communication={
                'serial-port': "/dev/ttyUSB0"
            }
        )
        preprocessing.pipeline = [
            SignalCheck(
                action=lambda param, condition, data: print(
                    'Condition: %s\n'
                    '\tMessage:Oh my, something went wrong here!\n'
                    '\tParameter: \n'
                    '\t\t%s'
                    % (
                        condition,
                        param['parameter-1']
                    )
                ),
                action_parameters={
                    'parameter-1': 'Parameter 1!'
                },
                conditions={
                    'Is greater than 0': lambda data: max(data) > 0
                }
            ),
            Downsample(
                type='MEAN',
                period=100
            ),
            Detrend(
                type='LINEAR'
            ),
            Custom(
                process_parameters={
                    'period': 100,
                    'operation': 1
                },
                process=lambda parameters, data: DataFilter.perform_rolling_filter(
                    data,
                    parameters['period'],
                    parameters['operation']
                )
            ),
            BandFilter(
                type='BANDPASS',
                filter='BUTTERWORTH',
                order=1,
                sampling_frequency=board.get_sampling_rate(),
                center_frequency=10,
                band_width=10
            ),
            BandFilter(
                type='BANDPASS',
                filter='BUTTERWORTH',
                order=1,
                sampling_frequency=board.get_sampling_rate(),
                center_frequency=10,
                band_width=2
            ),
            CutOffFilter(
                type='LOWPASS',
                filter='BUTTERWORTH',
                order=1,
                sampling_frequency=board.get_sampling_rate(),
                cutoff_frequency=18
            ),
            CutOffFilter(
                type='HIGHPASS',
                filter='BUTTERWORTH',
                order=1,
                sampling_frequency=board.get_sampling_rate(),
                cutoff_frequency=2
            ),
            Denoise(
                type='WAVELET',
                wavelet='haar',
                decomposition_level=2
            ),
            Denoise(
                type='ENVIRONMENT',
                noise_type='SIXTY',
                sampling_frequency=board.get_sampling_rate()
            ),
            Smooth(
                type='MEAN',
                period=100
            )
        ]
        board.preprocessing = preprocessing
        return cls(
            board=board
        )

    def start(self):
        self.board.start_stream_callback(self._on_data)
        QtGui.QApplication.instance().exec_()

    def stop(self):
        self.board.close_session()

    def _on_data(self, new_data: NDArray[Float]):
        if self.data is None:
            self.data = new_data
        else:
            self.data = numpy.append(self.data, new_data, axis=1)
        self.graph.plot_data(self.data)
