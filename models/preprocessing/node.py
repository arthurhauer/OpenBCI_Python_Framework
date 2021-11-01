import abc


class PreProcessingNode:
    _type: str

    def __init__(self, parameters: dict) -> None:
        super().__init__()

    @abc.abstractmethod
    def process(self, data):
        raise NotImplementedError()
