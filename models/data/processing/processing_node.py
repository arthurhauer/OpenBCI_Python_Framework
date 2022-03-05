import abc


class ProcessingNode:
    _type: str

    def __init__(self, parameters: dict = {}) -> None:
        super().__init__()
        if 'type' in parameters:
            self._type = parameters['type']

    @classmethod
    @abc.abstractmethod
    def from_config_json(cls, parameters: dict):
        raise NotImplementedError()

    @abc.abstractmethod
    def process(self, data):
        raise NotImplementedError()
