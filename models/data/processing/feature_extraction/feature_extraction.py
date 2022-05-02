from typing import List

from config.configuration import Configuration
from models.data.processing.epoching.epoching import Epoching
from models.data.processing.feature_extraction.csp import CSP
from models.data.processing.feature_extraction.dummy import Dummy
from models.data.processing.feature_extraction.feature_extractor import FeatureExtractor
from models.data.processing.feature_extraction.type import FeatureExtractorType


class FeatureExtraction:

    @classmethod
    def from_config_json(cls, parameters: dict):
        if parameters is None:
            extractor = Dummy()
        if 'type' not in parameters:
            extractor = Dummy()
        else:
            extractor = cls._select_processor(parameters)
        return extractor

    @staticmethod
    def _select_processor(node_settings: dict) -> FeatureExtractor:
        extractor_type = FeatureExtractorType[node_settings['type']]
        parameters = node_settings['parameters']

        parameters['sampling-frequency'] = Configuration.get_sampling_frequency()
        parameters['epocher'] = Epoching.from_config_json(Configuration.get_epoching_settings())
        if extractor_type == FeatureExtractorType.PRELOADED:
            raise NotImplementedError("PRELOADED is not implemented yet")

        if extractor_type == FeatureExtractorType.CSP:
            return CSP.from_config_json(parameters)

        else:
            raise ValueError("Invalid feature extractor type " + node_settings['type'])
