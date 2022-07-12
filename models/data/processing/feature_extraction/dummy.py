import mne as mne
import numpy

from models.data.processing.epoching.epocher import Epocher
from models.data.processing.feature_extraction.feature_extractor import FeatureExtractor


class Dummy(FeatureExtractor):

    def __init__(self) -> None:
        super().__init__(type='Dummy', epocher=Epocher('Dummy', 1,1))

    @classmethod
    def from_config_json(cls, parameters: dict):
        return cls()

    def process(self, data, marker_index):
        pass

    def train(self, data, label):
        pass
