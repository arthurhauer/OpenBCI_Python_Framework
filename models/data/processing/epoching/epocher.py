import abc
from typing import Any


class Epocher:

    def __init__(self, type: str, sampling_rate:int) -> None:
        if type is None:
            raise ValueError('epoching.epocher.invalid.parameters.must.have.type')
        super().__init__({"type": type})

    @classmethod
    @abc.abstractmethod
    def from_config_json(cls, parameters: dict):
        raise NotImplementedError()

    @abc.abstractmethod
    def process(self, data, label) -> Any:
        raise NotImplementedError()
