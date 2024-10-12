import json
from application import Application


if __name__ == '__main__':
    configuration_file = open('config/configuration.json', 'r')
    config_data = json.load(configuration_file)
    configuration_file.close()
    Application(config_data)
