import time
import matplotlib.pyplot as plt
from nptyping import NDArray, Float

from board_communication.models.board_data import BoardData
from board_communication.open_bci_board import OpenBCIBoard

data = BoardData()


def on_data(new_data: BoardData):
    data.append_accelerometer_data(new_data.get_accelerometer_data().as_array())
    data.append_eeg_data(new_data.get_eeg_data())
    print(str(len(data.get_accelerometer_data().as_array()[0]))+'-'+str(len(data.get_eeg_data()[0])))
    
def plot_data(data:BoardData):
    plt.plot(data.get_eeg_data()[0])
    plt.show()

def main():
    board = OpenBCIBoard()
    board.start_stream_callback(on_data)
    time.sleep(5)
    board.close_session()
    plot_data(data)

if __name__ == "__main__":
    main()
