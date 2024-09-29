import threading
from typing import Final

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.utils.cue import Cue
from models.utils.duration import Duration


class Trial:
    """This class represents a trial. A trial is a specific event that you want to generate data for (e.g. Hand Grasp,
    Feet Movement, etc.). 

    :param name: The trial name defined by the user in the configuration file.
    :type name: str
    :param code: The code defined by the user in the configuration file.
    :type code: int
    :param duration: The trial duration defined by the user in the configuration file.
    :type duration: Duration
    :param cue: The trial cue defined by the user in the configuration file.
    :type cue: Cue

    The data generated is random, but it is restricted to the statistical parameters that you
    define. For example, if you define a mean of 5 seconds and a standard deviation of 1 second, the data generated
    will be random, but it will be restricted to the range of 4 to 6 seconds.

    ``configuration.json`` usage:

        **name** (*str*): Trial name.\n
        **code** (*int*): Trial code. Just a number that identifies the trial.\n
        **duration** (*Duration*): Trial duration. This class generates a random numbers based on the parameters
        that you define. It is defined by a dictionary containing the following parameters: \n
            **mean** (*float*): Mean value for the trial duration.\n
            **standard_deviation** (*float*): Standard deviation value for the trial duration.\n
            **maximum** (*float*): Maximum value for the trial duration.\n
            **minimum** (*float*): Minimum value for the trial duration.\n
        **cue** (*Cue*): Trial cue. This class executes a specific cue defined by the user in a different python file
        (e.g. Print a value, Save a velue in a file, etc.). It is defined by a dictionary containing the following parameters: \n
            **file** (*str*): Cue file path.\n
            **parameters** (*dict*): The parameters that will be passed to the cue function defined in **file** when it is executed.\n
        
    """
    _MODULE_NAME: Final[str] = 'utils.trial'

    def __init__(self, name: str, code: int, duration: Duration, cue: Cue) -> None:
        """Constructor method. Initializes and validates the parameters of the class.
        """
        super().__init__()
        self.name = name
        if name is None:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='name')
        if code is None:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='code')
        if len(name) == 0:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='name',
                                        cause='len==0')
        if duration is None:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='duration')
        if cue is None:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='cue')
        self.name = name
        self.code = code
        self.duration = duration
        self.cue = cue

    @classmethod
    def from_config_json(cls, parameters: dict):
        """Creates a new instance of this class and initializes it with the parameters that were passed to it.
        """
        name = parameters['name']
        if 'name' not in parameters:
            raise MissingParameterError(module=cls._MODULE_NAME,
                                        parameter='name',
                                        name='undefined')
        if 'code' not in parameters:
            raise MissingParameterError(module=cls._MODULE_NAME,
                                        parameter='code',
                                        name=name)
        if 'duration' not in parameters:
            raise MissingParameterError(module=cls._MODULE_NAME,
                                        parameter='duration',
                                        name=name)
        if 'cue' not in parameters:
            raise MissingParameterError(module=cls._MODULE_NAME,
                                        parameter='cue',
                                        name=name)

        parameters['duration']['name'] = name
        return cls(
            name=name,
            code=parameters['code'],
            duration=Duration.from_config_json(parameters['duration']),
            cue=Cue.from_config_json(parameters['cue'])
        )

    def start(self):
        """Starts the trial execution by executing the cue and starting a timer that will call the ``on_stop`` method
        when the trial duration is reached using the ``duration`` parameter.
        """
        self.cue.execute()
        timer = threading.Timer(self.duration.get_duration(), self.on_stop)
        timer.start()

    def on_stop(self):
        pass

    def __str__(self):
        return '{' + f'"name":"{self.name}","code":{self.code},"duration":{self.duration},"cue":{self.cue}' + '}'
