import time

from board_communication.open_bci_board import OpenBCIBoard


def main():
    board = OpenBCIBoard()
    board.start_stream()
    i = 0
    while i < 60:
        time.sleep(10)
        print(board.get_data())
        i += 10
    board.close_session()


if __name__ == "__main__":
    main()
