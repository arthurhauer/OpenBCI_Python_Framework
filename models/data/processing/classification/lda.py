from nptyping import ndarray
from numpy import array
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
        print("Process "+str(epoched_data.shape))
        # pass
        train_data = epoched_data.reshape(epoched_data.shape[0], epoched_data.shape[1]*epoched_data.shape[2])
        predicted = self.lda.predict(train_data)
        print(predicted)
        return predicted

    def _inner_train(self, epoched_data, label):
        # pass
        print("Train "+str(epoched_data.shape))
        train_data = epoched_data.reshape(epoched_data.shape[0], epoched_data.shape[1]*epoched_data.shape[2])
        self.lda = self.lda.fit(train_data, label)
