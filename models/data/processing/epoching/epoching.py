from config.configuration import Configuration
from models.data.processing.epoching.epocher import Epocher
from models.data.processing.epoching.trial_wise_epocher import TrialWiseEpocher
from models.data.processing.epoching.type import EpocherType


class Epoching:

    @classmethod
    def from_config_json(cls, parameters: dict):
        if parameters is None:
            raise ValueError("epoching.must.have.parameters")
        if 'type' not in parameters:
            raise ValueError("epoching.parameters.must.have.type")
        else:
            epocher = cls._select_processor(parameters)
        return epocher

    @staticmethod
    def _select_processor(node_settings: dict) -> Epocher:
        epocher_type = EpocherType[node_settings['type']]
        parameters = node_settings['parameters']

        parameters['sampling-frequency'] = Configuration.get_sampling_frequency()

        epocher = None
        if epocher_type == EpocherType.TRIAL:
            epocher = TrialWiseEpocher.from_config_json(parameters)

        elif epocher_type == EpocherType.CROPPED:
            raise NotImplementedError("CROPPED is not implemented yet")

        else:
            raise ValueError("Invalid epocher type " + node_settings['type'])

        return epocher
