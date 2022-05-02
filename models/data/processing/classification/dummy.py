from models.data.processing.classification.classifier import Classifier
from models.data.processing.epoching.epocher import Epocher


class Dummy(Classifier):

    def __init__(self) -> None:
        super().__init__(type='Dummy', epocher=Epocher('Dummy', 1))

    @classmethod
    def from_config_json(cls, parameters: dict):
        return cls()

    def process(self, data):
        pass

    def train(self, data, label):
        pass
