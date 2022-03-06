import numpy
import time
from brainflow import BoardShim, BrainFlowInputParams, BoardIds

from application import Application

if __name__ == "__main__":
    Application()
    # BoardShim.enable_dev_board_logger()
    #
    # params = BrainFlowInputParams()
    # params.serial_port = "COM4"
    #
    # board = BoardShim(BoardIds['CYTON_BOARD'], params)
    # board.prepare_session()
    #
    # board.start_stream(45000)
    # for i in range(10):
    #     time.sleep(1)
    #     board.insert_marker(i + 1)
    # data = board.get_board_data()
    # board.stop_stream()
    # board.release_session()
    #
    # print(data)
