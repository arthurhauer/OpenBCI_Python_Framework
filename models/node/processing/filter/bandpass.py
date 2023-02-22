import abc
from typing import Final, Tuple
from scipy.signal import butter

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.node.processing.filter.filter import Filter


class BandPass(Filter):
    _MODULE_NAME: Final[str] = 'node.processing.filter.bandpass'

    def _validate_parameters(self, parameters: dict):
        if 'low_cut_frequency_hz' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME,name=self.name,
                                        parameter='low_cut_frequency_hz')
        if 'high_cut_frequency_hz' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME,name=self.name,
                                        parameter='high_cut_frequency_hz')
        if 'order' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME,name=self.name,
                                        parameter='order')

        if type(parameters['low_cut_frequency_hz']) is not float and type(
                parameters['low_cut_frequency_hz']) is not int:
            raise InvalidParameterValue(module=self._MODULE_NAME,name=self.name,
                                        parameter='low_cut_frequency_hz',
                                        cause='must_be_number')

        if type(parameters['high_cut_frequency_hz']) is not float and type(
                parameters['high_cut_frequency_hz']) is not int:
            raise InvalidParameterValue(module=self._MODULE_NAME,name=self.name,
                                        parameter='high_cut_frequency_hz',
                                        cause='must_be_number')

        if type(parameters['order']) is not int:
            raise InvalidParameterValue(module=self._MODULE_NAME,name=self.name,
                                        parameter='order',
                                        cause='must_be_int')

    @abc.abstractmethod
    def _initialize_parameter_fields(self, parameters: dict):
        super()._initialize_parameter_fields(parameters)

    def _get_filter_coefficients(self, parameters: dict, sampling_frequency_hz: float) -> Tuple[list, list]:
        return butter(
            parameters['order'],
            [
                parameters['low_cut_frequency_hz'],
                parameters['high_cut_frequency_hz']
            ],
            fs=sampling_frequency_hz,
            btype='band',
            output='ba'
        )
