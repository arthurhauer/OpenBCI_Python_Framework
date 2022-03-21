import abc

from models.data.processing.epoching.epocher import Epocher
from models.data.processing.processing_node import ProcessingNode


class TrainableProcessingNode(ProcessingNode):

    def __init__(self, type: str, epocher: Epocher) -> None:
        super().__init__({'type': type})
        self.epocher = epocher
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
        if label is None:
            raise ValueError('data.processing.trainable.processing.node.train.must.have.label')
        if label < 0:
            raise ValueError('data.processing.trainable.processing.node.train.label.must.be.greater.than.zero')
        self._inner_train(self.epocher.process(data, label))
        self._trained = True

    @abc.abstractmethod
    def _inner_train(self, epoched_data):
        raise NotImplementedError()
