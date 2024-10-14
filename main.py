import json
import signal
import threading
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace

from application import Application



def get_execution_arguments() -> Namespace:
    parser = ArgumentParser(
        prog='main.py',
        description='Starts the application',
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--config',
        help='Path to the configuration file',
        type=str,
        default='config/configuration.json'
    )
    return parser.parse_args()


def get_config_path(args: Namespace) -> str:
    return args.config

def get_config_data(config_path:str):
    configuration_file = open(config_path, 'r')
    config_data = json.load(configuration_file)
    configuration_file.close()
    return config_data

if __name__ == '__main__':
    exec_args = get_execution_arguments()
    config_path = get_config_path(exec_args)
    config_data = get_config_data(config_path)
    app = Application(config_data)

    def signal_handler(sig, frame):
        print('Will dispose application')
        stop_event.set()

    signal.signal(signal.SIGINT, signal_handler)

    stop_event = threading.Event()

    # Use a loop to poll the event status
    while not stop_event.is_set():
        stop_event.wait(0.1)  # Check every 100ms

    app.dispose()