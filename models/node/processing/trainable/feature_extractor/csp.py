import abc
from typing import List, Final

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.node.processing.trainable.feature_extractor.trainable_feature_extractor import TrainableFeatureExtractor


class CSP(TrainableFeatureExtractor):
    _MODULE_NAME: Final[str] = 'node.processing.trainable.feature_extractor.csp'

    def __init__(self, parameters: dict):
        super().__init__(parameters)
        self._validate_parameters(parameters)
        self.number_of_components = parameters['number_of_components']

    @abc.abstractmethod
    def _validate_parameters(self, parameters: dict):
        super()._validate_parameters(parameters)
        if 'number_of_components' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME,
                                        parameter='number_of_components')
        if type(parameters['number_of_components']) is not int:
            raise InvalidParameterValue(module=self._MODULE_NAME,
                                        parameter='number_of_components',
                                        cause='must_be_int')
