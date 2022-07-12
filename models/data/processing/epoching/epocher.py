import abc
from typing import Any

from models.data.processing.processing_node import ProcessingNode


class Epocher(ProcessingNode):

    def __init__(self, type: str, sampling_rate: int, trial_length: int) -> None:
        if type is None:
            raise ValueError('epoching.epocher.invalid.parameters.must.have.type')
        if sampling_rate is None:
            raise ValueError('epoching.epocher.invalid.parameters.must.have.sampling.frequency')
        if sampling_rate <= 0:
            raise ValueError('epoching.epocher.invalid.parameters.sampling.frequency.must.be.greater.than.zero')
        if trial_length is None:
            raise ValueError('epoching.epocher.invalid.parameters.must.have.trial.length')
        if trial_length <= 0:
            raise ValueError('epoching.epocher.invalid.parameters.trial.length.must.be.greater.than.zero')
        self.sampling_rate = sampling_rate
        self.trial_length = trial_length
        super().__init__({"type": type})

    @classmethod
    @abc.abstractmethod
    def from_config_json(cls, parameters: dict):
        raise NotImplementedError()

    @abc.abstractmethod
    def process(self, data, label) -> Any:
        raise NotImplementedError()
