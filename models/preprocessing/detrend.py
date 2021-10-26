from models.preprocessing.node import PreProcessingNode


class Detrend(PreProcessingNode):
    def __init__(self, parameters: dict) -> None:
        super().__init__(parameters)
