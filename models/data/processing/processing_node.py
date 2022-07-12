import abc


class ProcessingNode:
    _type: str

    def __init__(self, parameters=None) -> None:
        super().__init__()
        if parameters is None:
            parameters = {}
        if 'type' in parameters:
            self._type = parameters['type']

    @classmethod
    @abc.abstractmethod
    def from_config_json(cls, parameters: dict):
        raise NotImplementedError()

    @abc.abstractmethod
    def process(self, data):
        raise NotImplementedError()
