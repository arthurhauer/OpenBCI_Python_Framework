from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

from models.data.processing.classification.classifier import Classifier
from models.data.processing.epoching.epocher import Epocher


class LDA(Classifier):

    def __init__(self, epocher: Epocher) -> None:
        super().__init__('LDA', epocher)
        self.lda = LinearDiscriminantAnalysis()

    @classmethod
    def from_config_json(cls, parameters: dict):
        if 'epocher' not in parameters:
            raise ValueError('processing.trainable.classifier.lda.parameters.must.have.epocher')
        return cls(parameters['epocher'])

    def _inner_process(self, epoched_data):
        pass
        # return self.lda.transform(epoched_data)

    def _inner_train(self, epoched_data,label):
        pass
        # self.lda = self.lda.fit(epoched_data, label)
