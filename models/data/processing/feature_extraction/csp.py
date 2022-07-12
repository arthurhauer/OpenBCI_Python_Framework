import mne as mne
import numpy
import numpy as np

from models.data.processing.epoching.epocher import Epocher
from models.data.processing.feature_extraction.feature_extractor import FeatureExtractor


class CSP(FeatureExtractor):

    def __init__(self, n_components: int, epocher: Epocher) -> None:
        super().__init__('CSP', epocher)
        if n_components <= 0:
            raise ValueError(
                'processing.trainable.feature.extractor.csp.parameters.n_components.must.be.greater.than.zero')
        self.n_components = n_components
        self.csp = mne.decoding.csp.CSP(n_components=self.n_components)

    @classmethod
    def from_config_json(cls, parameters: dict):
        if 'n-components' not in parameters:
            raise ValueError('processing.trainable.feature.extractor.csp.parameters.must.have.n-components')
        if 'epocher' not in parameters:
            raise ValueError('processing.trainable.feature.extractor.csp.parameters.must.have.epocher')
        return cls(
            n_components=parameters['n-components'],
            epocher=parameters['epocher']
        )

    def _inner_process(self, epoched_data):
        transformed = self.csp.transform(epoched_data)
        return transformed

    def _inner_train(self, epoched_data, labels):
        self.csp = self.csp.fit(epoched_data, labels)
