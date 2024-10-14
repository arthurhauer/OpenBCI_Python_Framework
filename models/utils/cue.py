import os
from threading import Thread
from typing import Any, Final

from models.exception.missing_parameter import MissingParameterError
from models.utils.script_execution import script_execute


class Cue:
    """This class executes a specific cue (a script/function) defined by the user in a different python file (e.g. Print a value, Save a
    velue in a file, etc.). The cue can be anything that the user wants to execute when the trial starts or ends.

    :param function: The function that will be executed when the cue is called.
    :type function: Any
    :param parameters: The parameters that will be passed to the cue function when it is executed.
    :type parameters: dict

    :raises MissingParameterError: The ``function`` parameter is required.

    ``config.json`` example:
    
        **file** (*str*): Cue file path.\n
        **parameters** (*dict*): The parameters that will be passed to the cue function defined in **file** when it is executed. This can 
        be anything that the user needs to pass to the cue function.\n

    """
    _MODULE_NAME: Final[str] = 'utils.cue'

    def __init__(self, filename: str, function: Any, parameters: dict) -> None:
        """Constructor method. Initializes and validates the parameters of the class.
        """
        super().__init__()
        if function is None:
            raise MissingParameterError(module=self._MODULE_NAME,
                                        name='cue',
                                        parameter='function')
        if parameters is None:
            parameters = {}
        self._filename = filename
        self._function = function
        self._function_parameters = parameters

    @classmethod
    def from_config_json(cls, parameters: dict):
        """Creates a new instance of this class and initializes it with the parameters that were passed to it.
        """
        if 'file' not in parameters:
            raise MissingParameterError(module=cls._MODULE_NAME,
                                        name='cue',
                                        parameter='file')
        if 'parameters' not in parameters:
            cue_parameters = {}
        else:
            cue_parameters = parameters['parameters']
        cue_function_path = parameters['file']
        _locals = script_execute(parameters['file'])
        if 'custom_cue' not in _locals:
            raise ValueError(
                'session.trial.cue.custom_cue.not.defined.in.script.%s' % cue_function_path)
        return cls(
            filename=parameters['file'],
            function=_locals['custom_cue'],
            parameters=cue_parameters
        )

    def _run_function(self):
        """Runs the cue function.
        """
        self._function(self._function_parameters)

    def execute(self):
        """Executes the cue function with the parameters that were passed to it.
        """
        thread = Thread(target=self._run_function)
        thread.start()
        # thread.join()

    def __str__(self):
        return '{' + f'"file":{self._filename},"parameters":{self._function_parameters}' + '}'
