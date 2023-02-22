from typing import Final

from scipy import stats

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError


class Duration:
    _MODULE_NAME: Final[str] = 'utils.duration'

    def __init__(self, mean: float, standard_deviation: float, maximum: float, minimum: float) -> None:
        super().__init__()
        if mean is None:
            raise MissingParameterError(module=self._MODULE_NAME,name=self.name,
                                        parameter='mean')
        if standard_deviation is None:
            raise MissingParameterError(module=self._MODULE_NAME,name=self.name,
                                        parameter='standard_deviation')
        if maximum is None:
            raise MissingParameterError(module=self._MODULE_NAME,name=self.name,
                                        parameter='maximum')
        if minimum is None:
            raise MissingParameterError(module=self._MODULE_NAME,name=self.name,
                                        parameter='minimum')
        if mean <= 0:
            raise InvalidParameterValue(module=self._MODULE_NAME,name=self.name,
                                        parameter='mean',
                                        cause='<=0')
        if standard_deviation <= 0:
            raise InvalidParameterValue(module=self._MODULE_NAME,name=self.name,
                                        parameter='standard_deviation',
                                        cause='<=0')
        if maximum <= 0:
            raise InvalidParameterValue(module=self._MODULE_NAME,name=self.name,
                                        parameter='maximum',
                                        cause='<=0')
        if maximum < mean:
            raise InvalidParameterValue(module=self._MODULE_NAME,name=self.name,
                                        parameter='maximum',
                                        cause='<mean')
        if minimum <= 0:
            raise InvalidParameterValue(module=self._MODULE_NAME,name=self.name,
                                        parameter='minimum',
                                        cause='<=0')
        if minimum > mean:
            raise InvalidParameterValue(module=self._MODULE_NAME,name=self.name,
                                        parameter='minimum',
                                        cause='>mean')
        self.mean = mean
        self.standard_deviation = standard_deviation
        self.maximum = maximum
        self.minimum = minimum
        self._distribution = stats.truncnorm((self.minimum - self.mean) / self.standard_deviation,
                                             (self.maximum - self.mean) / self.standard_deviation, loc=self.mean,
                                             scale=self.standard_deviation)

    @classmethod
    def from_config_json(cls, parameters: dict):
        if 'mean' not in parameters:
            raise MissingParameterError(module=cls._MODULE_NAME,
                                        parameter='mean')
        if 'standard_deviation' not in parameters:
            raise MissingParameterError(module=cls._MODULE_NAME,
                                        parameter='standard_deviation')
        if 'maximum' not in parameters:
            raise MissingParameterError(module=cls._MODULE_NAME,
                                        parameter='maximum')
        if 'minimum' not in parameters:
            raise MissingParameterError(module=cls._MODULE_NAME,
                                        parameter='minimum')
        return cls(
            mean=parameters['mean'],
            standard_deviation=parameters['standard_deviation'],
            maximum=parameters['maximum'],
            minimum=parameters['minimum']
        )

    def get_duration(self) -> float:
        return self._distribution.rvs(1)[0]
