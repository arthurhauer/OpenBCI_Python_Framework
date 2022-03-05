import abc

from models.data.processing.trainable_processing_node import TrainableProcessingNode


class FeatureExtractor(TrainableProcessingNode):

    def __init__(self, parameters=None) -> None:
        if parameters is None:
            parameters = {}
        if 'type' not in parameters:
            raise ValueError('processing.trainable.feature.extractor.parameters.must.have.type')
        super().__init__(parameters=parameters)

    @classmethod
    @abc.abstractmethod
    def from_config_json(cls, parameters: dict):
        if 'parameters' not in parameters:
            raise ValueError('processing.trainable.feature.extractor.parameters.must.have.parameters')

    @abc.abstractmethod
    def process(self, data):
        raise NotImplementedError()

    @abc.abstractmethod
    def train(self, data, label):
        raise NotImplementedError()
