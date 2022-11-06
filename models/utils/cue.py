import os
from typing import Any, Final

from models.exception.missing_parameter import MissingParameterError
from models.utils.script_execution import script_execute


class Cue:
    _MODULE_NAME: Final[str] = 'utils.cue'

    def __init__(self, function: Any, parameters: dict) -> None:
        super().__init__()
        if function is None:
            raise MissingParameterError(module=self._MODULE_NAME,
                                        parameter='function')
        if parameters is None:
            parameters = {}
        self._function = function
        self._function_parameters = parameters

    @classmethod
    def from_config_json(cls, parameters: dict):
        if 'file' not in parameters:
            raise MissingParameterError(module=cls._MODULE_NAME,
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
            function=_locals['custom_cue'],
            parameters=cue_parameters
        )

    def execute(self):
        self._function(self._function_parameters)
