import abc

import numpy

from models.data.processing.epoching.epocher import Epocher
from models.data.processing.trainable_processing_node import TrainableProcessingNode


class Classifier(TrainableProcessingNode):

    def __init__(self, type: str, epocher: Epocher) -> None:
        super().__init__(type=type, epocher=epocher)

    @classmethod
    @abc.abstractmethod
    def from_config_json(cls, parameters: dict):
        raise NotImplementedError()

    def _append_classified(self, data, classified):
        data = numpy.vstack([data, classified])

    @abc.abstractmethod
    def _inner_process(self, epoched_data):
        raise NotImplementedError()

    @abc.abstractmethod
    def _inner_train(self, epoched_data, labels):
        raise NotImplementedError()
