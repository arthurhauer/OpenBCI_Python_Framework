from brainflow import DataFilter, AggOperations

from models.preprocessing.node import PreProcessingNode


class Smooth(PreProcessingNode):

    def __init__(self, type: str, period: int) -> None:
        if type is None:
            raise Exception('preprocessing.smooth.invalid.parameters.must.have.type')
        try:
            self._type = type
            self._operation: AggOperations = AggOperations[self._type]
        except KeyError:
            raise KeyError('preprocessing.smooth.invalid.parameters.type.invalid.%s' % self._type)
        if period is None:
            raise Exception('preprocessing.smooth.invalid.parameters.must.have.period')
        if period <= 0:
            raise Exception('preprocessing.smooth.invalid.parameters.period.must.be.greater.than.zero')
        super().__init__({'type': type})
        self._period: int = period

    @classmethod
    def from_config_json(cls, parameters: dict):
        if 'type' not in parameters:
            raise Exception('preprocessing.smooth.invalid.parameters.must.have.type')
        if 'period' not in parameters:
            raise Exception('preprocessing.smooth.invalid.parameters.must.have.period')
        return cls(
            type=parameters['type'],
            period=parameters['period']
        )

    def process(self, data):
        for channel in data:
            channel = DataFilter.perform_rolling_filter(channel, self._period, self._operation)
