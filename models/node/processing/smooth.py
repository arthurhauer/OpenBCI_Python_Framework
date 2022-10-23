from abc import ABC

from brainflow import DataFilter, AggOperations

from models.node.processing.processing_node import ProcessingNode


class Smooth(ProcessingNode):

    def _is_next_node_call_enabled(self) -> bool:
        pass

    def _is_processing_condition_satisfied(self) -> bool:
        pass

    def _process(self, data: list) -> list:
        pass

    def __init__(self, parameters: dict) -> None:
        super().__init__(parameters)
        if 'operation' not in parameters:
            raise ValueError('error'
                             '.missing'
                             '.node'
                             '.processing'
                             '.smooth'
                             '.operation')
        if 'period' not in parameters:
            raise ValueError('error'
                             '.missing'
                             '.node'
                             '.processing'
                             '.smooth'
                             '.period')
        try:
            self._operation: AggOperations = AggOperations[parameters['operation']]
        except KeyError:
            raise ValueError('error'
                             '.invalid'
                             '.value'
                             '.node'
                             '.processing'
                             '.smooth'
                             '.operation')
        if parameters['period'] <= 0:
            ValueError('error'
                       '.invalid'
                       '.value'
                       '.node'
                       '.processing'
                       '.smooth'
                       '.period'
                       '.must_be_greater_than_zero')
        self._period: int = parameters['period']

    @classmethod
    def from_config_json(cls, parameters: dict):
        return cls(parameters)

    def process(self, data):
        for channel in data:
            DataFilter.perform_rolling_filter(channel, self._period, self._operation)
