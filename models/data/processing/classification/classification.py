from typing import List

from config.configuration import Configuration
from models.data.processing.classification.classifier import Classifier
from models.data.processing.classification.lda import LDA
from models.data.processing.feature_extraction.csp import CSP
from models.data.processing.feature_extraction.dummy import Dummy
from models.data.processing.feature_extraction.feature_extractor import FeatureExtractor
from models.data.processing.feature_extraction.type import FeatureExtractorType


class Classification:

    @classmethod
    def from_config_json(cls, parameters: dict):
        if parameters is None:
            classifier = Dummy()
        if 'type' not in parameters:
            classifier = Dummy()
        else:
            classifier = cls._select_processor(parameters)
        return classifier

    @staticmethod
    def _select_processor(node_settings: dict) -> Classifier:
        classifier_type = FeatureExtractorType[node_settings['type']]
        parameters = node_settings['parameters']

        parameters['sampling-frequency'] = Configuration.get_sampling_frequency()

        classifier = None
        if classifier_type == FeatureExtractorType.PRELOADED:
            raise NotImplementedError("PRELOADED is not implemented yet")

        if classifier_type == FeatureExtractorType.LDA:
            classifier = LDA.from_config_json(parameters)

        else:
            raise ValueError("Invalid classifier type " + node_settings['type'])

        return classifier
