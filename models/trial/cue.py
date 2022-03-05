import os
from typing import Any

from globals.globals import TRIAL_CUE_FUNCTION_DIR
from models.utils.utils import script_execute


class Cue:
    def __init__(self, function: Any, parameters: dict) -> None:
        super().__init__()
        if function is None:
            raise ValueError('trial.sequence.cue.must.have.function')
        if parameters is None:
            parameters = {}
        self._function = function
        self._function_parameters = parameters

    @classmethod
    def from_config_json(cls, parameters: dict):
        if 'file' not in parameters:
            raise ValueError('trial.sequence.cue.must.have.file')
        if 'parameters' not in parameters:
            cue_parameters = {}
        else:
            cue_parameters = parameters['parameters']
        cue_function_path = os.path.join(TRIAL_CUE_FUNCTION_DIR, parameters['file'])
        _locals = script_execute(cue_function_path)
        if 'custom_cue' not in _locals:
            raise ValueError(
                'trial.sequence.cue.custom_cue.not.defined.in.script.%s' % cue_function_path)
        return cls(
            function=_locals['custom_cue'],
            parameters=cue_parameters
        )

    def execute(self):
        self._function(self._function_parameters)
