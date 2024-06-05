import json
import signal
from threading import Thread
from flask import Flask, request
from application import Application

app = Flask(__name__)

application = None
interface_thread = None

signal.signal(signal.SIGINT, lambda x, y: stop())
signal.signal(signal.SIGTERM, lambda x, y: stop())


def run_app(configuration):
    global application
    application = Application(configuration)


@app.route('/start', methods=['POST'])
def start():
    global application
    global interface_thread
    if application is not None:
        return 'Application already running'
    config = request.get_json()
    interface_thread = Thread(target=run_app, args=(config,), daemon=True)
    interface_thread.start()
    return 'Application running'


@app.route('/stop', methods=['GET'])
def stop():
    global application
    global interface_thread
    if application is None:
        return 'No application running'

    application.dispose()
    interface_thread.join()
    return 'Application stopped'

# if __name__ == '__main__':
#     app.run(debug=True, host='127.0.0.1', port=8001)

if __name__ == '__main__':
    configuration_file = open('config/configuration.json', 'r')
    config_data = json.load(configuration_file)
    configuration_file.close()
    Application(config_data)