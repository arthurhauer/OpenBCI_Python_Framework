import abc

from models.data.processing.epoching.epocher import Epocher
from models.data.processing.processing_node import ProcessingNode


class TrainableProcessingNode(ProcessingNode):

    def __init__(self, type: str, epocher: Epocher) -> None:
        if type is None:
            raise ValueError('processing.trainable.feature.extractor.parameters.must.have.type')
        if epocher is None:
            raise ValueError('processing.trainable.feature.extractor.parameters.must.have.type')
        super().__init__({'type': type})
        self.epocher = epocher
        self._trained = False

    @classmethod
    @abc.abstractmethod
    def from_config_json(cls, parameters: dict):
        raise NotImplementedError()

    def process(self, data, marker_index):
        if not self._trained:
            return
        if data is None:
            return
        if marker_index is None:
            raise ValueError('data.processing.trainable.processing.node.process.must.have.marker_index')
        if marker_index < 0:
            raise ValueError('data.processing.trainable.processing.node.process.marker_index.must.be.greater.than.zero')
        epoched_data, _ = self.epocher.process(data, marker_index)
        if len(epoched_data[0][0]) != 100:
            print(len(epoched_data[0][0]))
            return
        predicted = self._inner_process(epoched_data)
        return predicted
        # print(predicted)


    @abc.abstractmethod
    def _inner_process(self, epoched_data):
        raise NotImplementedError()

    def train(self, data, label):
        if data is None:
            return
        if label is None:
            raise ValueError('data.processing.trainable.processing.node.train.must.have.label')
        if label < 0:
            raise ValueError('data.processing.trainable.processing.node.train.label.must.be.greater.than.zero')
        epoched_data, labels = self.epocher.process(data, label)
        self._inner_train(epoched_data, labels)
        self._trained = True

    @abc.abstractmethod
    def _inner_train(self, epoched_data, labels):
        raise NotImplementedError()
