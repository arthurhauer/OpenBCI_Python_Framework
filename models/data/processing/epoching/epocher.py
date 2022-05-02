import abc
from typing import Any

from models.data.processing.processing_node import ProcessingNode


class Epocher(ProcessingNode):

    def __init__(self, type: str, sampling_rate: int) -> None:
        if type is None:
            raise ValueError('epoching.epocher.invalid.parameters.must.have.type')
        if sampling_rate is None:
            raise ValueError('epoching.epocher.invalid.parameters.must.have.sampling.frequency')
        if sampling_rate <= 0:
            raise ValueError('epoching.epocher.invalid.parameters.sampling.frequency.must.be.greater.than.zero')
        self.sampling_rate = sampling_rate
        super().__init__({"type": type})

    @classmethod
    @abc.abstractmethod
    def from_config_json(cls, parameters: dict):
        raise NotImplementedError()

    @abc.abstractmethod
    def process(self, data, label) -> Any:
        raise NotImplementedError()
