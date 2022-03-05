from brainflow import DataFilter, DetrendOperations

from models.preprocessing.node import PreProcessingNode


class Detrend(PreProcessingNode):
    def __init__(self, type: str) -> None:
        super().__init__()
        if type is None:
            raise Exception('preprocessing.detrend.invalid.parameters.must.have.type')
        try:
            self._type = type
            self._detrend_type: DetrendOperations = DetrendOperations[self._type]
        except KeyError:
            raise KeyError('preprocessing.detrend.invalid.parameters.type.invalid.%s' % self._type)

    @classmethod
    def from_config_json(cls, parameters: dict):
        if 'type' not in parameters:
            raise Exception('preprocessing.detrend.invalid.parameters.must.have.type')
        return cls(
            type=parameters['type']
        )

    def process(self, data):
        for channel in data:
            DataFilter.detrend(data, self._detrend_type)
