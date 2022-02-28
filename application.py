from models.data.board_data import BoardData
from board_communication.open_bci_board import OpenBCIBoard
from graph.graph import Graph
from pyqtgraph.Qt import QtGui

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
        preprocessing.pipeline = []
        cls.__init__(
            board=OpenBCIBoard(
                preprocessing=preprocessing,
                log_level="INFO",
                board="SYNTHETIC_BOARD"
            )
        )

    @classmethod
    def from_config_json(cls):
        cls.__init__(
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
