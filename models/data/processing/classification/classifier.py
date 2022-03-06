import abc

import numpy

from models.data.processing.trainable_processing_node import TrainableProcessingNode


class Classifier(TrainableProcessingNode):

    def __init__(self, parameters=None) -> None:
        if parameters is None:
            parameters = {}
        if 'type' not in parameters:
            raise ValueError('processing.trainable.classifier.parameters.must.have.type')
        super().__init__(parameters=parameters)

    @classmethod
    @abc.abstractmethod
    def from_config_json(cls, parameters: dict):
        raise NotImplementedError()

    def _append_classified(self, data, classified):
        data = numpy.vstack([data, classified])

    @abc.abstractmethod
    def process(self, data):
        raise NotImplementedError()

    @abc.abstractmethod
    def train(self, data, label):
        raise NotImplementedError()
