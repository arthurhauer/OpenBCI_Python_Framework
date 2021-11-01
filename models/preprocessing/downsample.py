from brainflow import DataFilter, AggOperations

from models.preprocessing.node import PreProcessingNode


class Downsample(PreProcessingNode):

    def __init__(self, parameters: dict) -> None:
        super().__init__(parameters)
        if 'type' not in parameters:
            raise Exception('preprocessing.downsample.invalid.parameters.must.have.type')
        if 'period' not in parameters:
            raise Exception('preprocessing.downsample.invalid.parameters.must.have.period')
        self._type: AggOperations = AggOperations[parameters['type']]
        self._period: int = parameters['period']
        self.process = self._set_downsample

    def _set_downsample(self, data):
        data = DataFilter.perform_downsampling(data, self._period, self._type)
