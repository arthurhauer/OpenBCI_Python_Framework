import mne as mne
import numpy
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

from models.data.processing.classification.classifier import Classifier


class LDA(Classifier):

    def __init__(self) -> None:
        super().__init__({'type': 'LDA'})
        self.lda = LinearDiscriminantAnalysis()

    @classmethod
    def from_config_json(cls, parameters: dict):
        return cls()

    def process(self, data):
        if super()._trained:
            super()._append_classified(data, self.lda.transform(data))
        else:
            super()._append_classified(data, numpy.zeros((1, len(data[0]))))

    def train(self, data, label):
        super()._trained = False
        self.lda = self.lda.fit(data, label)
        super()._append_classified(data, numpy.zeros((1, len(data[0]))))
        super().train(data, label)
