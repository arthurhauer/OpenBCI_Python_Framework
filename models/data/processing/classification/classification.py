from config.configuration import Configuration
from models.data.processing.classification.classifier import Classifier
from models.data.processing.classification.dummy import Dummy
from models.data.processing.classification.lda import LDA
from models.data.processing.classification.type import ClassifierType
from models.data.processing.epoching.epoching import Epoching


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
        classifier_type = ClassifierType[node_settings['type']]
        parameters = node_settings['parameters']

        parameters['sampling-frequency'] = Configuration.get_sampling_frequency()
        parameters['epocher']=Epoching.from_config_json(Configuration.get_epoching_settings())
        if classifier_type == ClassifierType.PRELOADED:
            raise NotImplementedError("PRELOADED is not implemented yet")

        elif classifier_type == ClassifierType.LDA:
            return LDA.from_config_json(parameters)

        else:
            raise ValueError("Invalid classifier type " + node_settings['type'])
