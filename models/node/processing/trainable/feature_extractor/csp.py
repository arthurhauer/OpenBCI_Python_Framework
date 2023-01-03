import abc
from typing import List, Final

import mne.decoding
import numpy as np

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.processing.trainable.feature_extractor.trainable_feature_extractor import TrainableFeatureExtractor


class CSP(TrainableFeatureExtractor):
    _MODULE_NAME: Final[str] = 'node.processing.trainable.feature_extractor.csp'

    def __init__(self, parameters: dict):
        super().__init__(parameters)
        self._validate_parameters(parameters)
        self.number_of_components = parameters['number_of_components']
        self.csp: mne.decoding.CSP = mne.decoding.CSP(n_components=self.number_of_components)

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

    @abc.abstractmethod
    def _is_training_condition_satisfied(self) -> bool:
        return self._input_buffer[self.INPUT_DATA].get_data_count() > 0 \
               and self._input_buffer[self.INPUT_LABEL].get_data_count() > 0

    @abc.abstractmethod
    def _should_retrain(self) -> bool:
        return False

    def _extract_data(self, data: FrameworkData) -> FrameworkData:
        extracted_data = self.csp.transform(np.asarray(data.get_data_as_2d_array()))
        extracted_data = np.moveaxis(extracted_data, 1, 0)
        formatted_data = FrameworkData(sampling_frequency_hz=data.sampling_frequency,
                                       channels=[f'source_{i}' for i in range(1, self.number_of_components)])
        return formatted_data.input_2d_data(extracted_data)

    def _train(self, data: FrameworkData, label: FrameworkData):
        formatted_data = np.asarray(data.get_data_as_2d_array())
        formatted_data = np.moveaxis(formatted_data, 1, 0)
        formatted_label = []
        for epoch in label.get_data_single_channel():
            formatted_label.append(max(epoch))
        formatted_label = np.asarray(formatted_label)
        self.csp.fit(formatted_data, formatted_label)
