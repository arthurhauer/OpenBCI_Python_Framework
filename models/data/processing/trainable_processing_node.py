import abc

from models.data.processing.processing_node import ProcessingNode


class TrainableProcessingNode(ProcessingNode):

    def __init__(self, parameters: dict = {}) -> None:
        super().__init__(parameters=parameters)
        self._trained = False

    @classmethod
    @abc.abstractmethod
    def from_config_json(cls, parameters: dict):
        raise NotImplementedError()

    @abc.abstractmethod
    def process(self, data):
        raise NotImplementedError()

    @abc.abstractmethod
    def train(self, data, label):
        self._trained = True
