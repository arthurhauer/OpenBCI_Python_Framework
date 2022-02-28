from models.data.board_data import BoardData
from board_communication.open_bci_board import OpenBCIBoard
from graph.graph import Graph
from pyqtgraph.Qt import QtGui

from models.preprocessing.custom import Custom
from models.preprocessing.detrend import Detrend
from models.preprocessing.downsample import Downsample
from models.preprocessing.signal_check import SignalCheck
from preprocessing.preprocessing import PreProcessing


class Application:

    def __init__(self, board: OpenBCIBoard) -> None:
        super().__init__()
        # self.gui_thread = Thread(target=self._exec_app)
        self.board = board
        self.data = BoardData(self.board.get_eeg_channel_names())
        self.graph = Graph(self.board.get_sampling_rate(), self.board.get_eeg_channel_names())

    @classmethod
    def as_sdk(cls):
        preprocessing: PreProcessing = PreProcessing()
        from brainflow import DataFilter
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
            )
        ]
        return cls(
            board=OpenBCIBoard(
                preprocessing=preprocessing,
                log_level="INFO",
                board="SYNTHETIC_BOARD"
            )
        )

    @classmethod
    def from_config_json(cls):
        return cls(
            board=OpenBCIBoard.from_config_json()
        )

    def _exec_app(self):
        QtGui.QApplication.instance().exec_()

    def start(self):
        self.board.start_stream_callback(self._on_data)
        # self.gui_thread.start()
        self._exec_app()

    def stop(self):
        self.board.close_session()
        # self.gui_thread.join(150)

    def _on_data(self, new_data: BoardData):
        self.data.append_new_data(new_data)
        self.graph.plot_data(self.data)
