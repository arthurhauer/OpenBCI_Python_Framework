import abc
from typing import Final, Any

import mne.decoding
import numpy as np
from sklearn.base import TransformerMixin, BaseEstimator

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.processing.trainable.feature_extractor.sklearn_feature_extractor import SKLearnFeatureExtractor


class CSP(SKLearnFeatureExtractor):
    _MODULE_NAME: Final[str] = 'node.processing.trainable.feature_extractor.csp'

    def _initialize_parameter_fields(self, parameters: dict):
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

    def _initialize_trainable_processor(self) -> (TransformerMixin, BaseEstimator):
        return mne.decoding.CSP(n_components=self.number_of_components)

    @abc.abstractmethod
    def _should_retrain(self) -> bool:
        return False

    @abc.abstractmethod
    def _is_next_node_call_enabled(self) -> bool:
        return True

    def _format_processed_data(self, processed_data: Any, sampling_frequency: float) -> FrameworkData:
        processed_data = np.moveaxis(processed_data, 1, 0)
        formatted_data = FrameworkData(sampling_frequency_hz=sampling_frequency,
                                       channels=[f'source_{i}' for i in range(1, self.number_of_components+1)])
        formatted_data.input_2d_data(processed_data)
        return formatted_data
