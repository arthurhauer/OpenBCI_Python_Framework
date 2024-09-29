from typing import Final

from scipy import stats

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError


class Duration:
    """This class generates a random number based on the parameters that you define. The data generated is random, but
    it is restricted to the statistical parameters that you define. For example, if you define a mean of 5 seconds and a
    standard deviation of 1 second, the data generated will be random, but it will be restricted to the range of 4 to 6
    seconds.

    :param mean: Mean value for the trial duration.
    :type mean: float
    :param standard_deviation: Standard deviation value for the trial duration.
    :type standard_deviation: float
    :param maximum: Maximum value for the trial duration.
    :type maximum: float
    :param minimum: Minimum value for the trial duration.
    :type minimum: float

    ``configuration.json`` usage:

        **mean** (*float*): Mean value for the trial duration.\n
        **standard_deviation** (*float*): Standard deviation value for the trial duration.\n
        **maximum** (*float*): Maximum value for the trial duration.\n
        **minimum** (*float*): Minimum value for the trial duration.\n
    
    """
    _MODULE_NAME: Final[str] = 'utils.duration'

    def __init__(self, name:str, mean: float, standard_deviation: float, maximum: float = None, minimum: float= None) -> None:
        """Constructor method. Initializes and validates the parameters of the class.
        The self._distribution variable is used to generate the random numbers. It uses the scypy.stats.truncnorm
        function to generate the random numbers in a truncated normal distribution. The truncated normal distribution
        is used because it restricts the random numbers to the range that you define.

        :param mean: Mean value for the trial duration.
        :type mean: float
        :param standard_deviation: Standard deviation value for the trial duration.
        :type standard_deviation: float
        :param maximum: Maximum value for the trial duration.
        :type maximum: float
        :param minimum: Minimum value for the trial duration.
        :type minimum: float

        :raises MissingParameterError: The ``mean`` and ``standard_deviation`` parameters are required. The `maximum`` and ``minimum`` parameters are required only when ``standard_deviation`` > 0.
        :raises InvalidParameterValue: The ``mean``, ``standard_deviation``, ``maximum`` and ``minimum`` parameters must be greater than 0.
        :raises InvalidParameterValue: The ``maximum`` parameter must be greater than the ``mean`` parameter.
        :raises InvalidParameterValue: The ``minimum`` parameter must be less than the ``mean`` parameter.

        :return: A new instance of ``Duration``.
        """
        super().__init__()
        self.name = name
        if mean is None:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='mean')
        if standard_deviation is None:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='standard_deviation')

        if mean <= 0:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='mean',
                                        cause='<=0')
        if standard_deviation < 0:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='standard_deviation',
                                        cause='<0')

        self.mean = mean
        self.standard_deviation = standard_deviation

        if standard_deviation > 0:

            if maximum is None:
                raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                            parameter='maximum')
            if minimum is None:
                raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                            parameter='minimum')
            if maximum <= 0:
                raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                            parameter='maximum',
                                            cause='<=0')
            if maximum < mean:
                raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                            parameter='maximum',
                                            cause='<mean')
            if minimum <= 0:
                raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                            parameter='minimum',
                                            cause='<=0')
            if minimum > mean:
                raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                            parameter='minimum',
                                            cause='>mean')

            self.maximum = maximum
            self.minimum = minimum
            self._distribution = stats.truncnorm((self.minimum - self.mean) / self.standard_deviation,
                                                 (self.maximum - self.mean) / self.standard_deviation, loc=self.mean,
                                                 scale=self.standard_deviation)

    @classmethod
    def from_config_json(cls, parameters: dict):
        """Creates a new instance of this class and initializes it with the parameters that were passed to it.
        
        :param parameters: The parameters that will be passed to the node. This comes from the configuration file.
        :type parameters: dict

        :raises MissingParameterError: The ``mean`` and ``standard_deviation`` parameters are required. The `maximum`` and ``minimum`` parameters are required only when ``standard_deviation`` > 0.

        :return: A new instance of this class.
        """
        if 'name' not in parameters:
            raise MissingParameterError(module=cls._MODULE_NAME,
                                        parameter='name',
                                        name='undefined')
        name = parameters['name']
        if 'mean' not in parameters:
            raise MissingParameterError(module=cls._MODULE_NAME,
                                        parameter='mean',
                                        name=name)
        if 'standard_deviation' not in parameters:
            raise MissingParameterError(module=cls._MODULE_NAME,
                                        parameter='standard_deviation',
                                        name=name)
        maximum_parameter = None
        minimum_parameter = None
        if parameters['standard_deviation'] > 0:
            if 'maximum' not in parameters:
                raise MissingParameterError(module=cls._MODULE_NAME,
                                            parameter='maximum',
                                            name=name)
            if 'minimum' not in parameters:
                raise MissingParameterError(module=cls._MODULE_NAME,
                                            parameter='minimum',
                                            name=name)
            maximum_parameter = parameters['maximum']
            minimum_parameter = parameters['minimum']
        return cls(
            name=name,
            mean=parameters['mean'],
            standard_deviation=parameters['standard_deviation'],
            maximum=maximum_parameter,
            minimum=minimum_parameter
        )

    def get_duration(self) -> float:
        """Returns a random number based on the parameters that you defined when you created the instance of this class.
        """
        if self.standard_deviation == 0:
            return self.mean
        return self._distribution.rvs(1)[0]

    def __str__(self):
        return '{' + f'"mean":{self.mean},"standard_deviation":{self.standard_deviation},"maximum":{self.maximum},"minimum":{self.minimum}' + '}'
