import os.path

import numpy as np

from globals.globals import SIGNAL_CHECK_ACTION_DIR
from models.data.processing.processing_node import ProcessingNode
from models.utils.utils import script_execute


class SignalCheck(ProcessingNode):

    def __init__(self, action, action_parameters: dict, conditions: dict) -> None:
        super().__init__()
        self._action = action
        self._action_parameters = action_parameters
        self._conditions = conditions

    @classmethod
    def from_predefined_conditions(cls, action, action_parameters, power_grid_frequency: float, min_amplitude: float,
                                   min_rms: float):
        # TODO Include powergrid frequency check
        return cls(
            action=action,
            action_parameters=action_parameters,
            conditions={
                'amplitude': lambda data: (max(data) - min(data)) < min_amplitude,
                'rms': lambda data: (np.sqrt(np.mean(data ** 2))) < min_rms,
                'frequency': lambda data: False
            }
        )

    @classmethod
    def from_config_json(cls, parameters: dict):
        if 'action' not in parameters:
            raise Exception('preprocessing.signal.check.invalid.parameters.must.have.action')
        if 'file' not in parameters['action']:
            raise Exception('preprocessing.signal.check.invalid.parameters.must.have.action.file')
        if 'parameters' not in parameters['action']:
            raise Exception('preprocessing.signal.check.invalid.parameters.must.have.action.parameters')
        if 'power-grid-frequency' not in parameters:
            raise Exception('preprocessing.signal.check.invalid.parameters.must.have.power-grid-frequency')
        if 'min-amplitude' not in parameters:
            raise ValueError('preprocessing.signal.check.invalid.parameters.must.have.min-amplitude')
        if 'min-rms' not in parameters:
            raise ValueError('preprocessing.signal.check.invalid.parameters.must.have.min-rms')

        action_path = os.path.join(SIGNAL_CHECK_ACTION_DIR, parameters['action']['file'])

        _locals = script_execute(action_path)

        if 'custom_action' not in _locals:
            raise ValueError(
                'preprocessing.signal.check.invalid.parameters.custom_action.not.defined.in.script.%s' % action_path)

        if 'parameters' not in parameters['action']:
            action_parameters = {}
        else:
            action_parameters = parameters['action']['parameters']

        return cls.from_predefined_conditions(
            action=_locals['custom_action'],
            action_parameters=action_parameters,
            power_grid_frequency=parameters['power-grid-frequency'],
            min_amplitude=parameters['min-amplitude'],
            min_rms=parameters['min-rms']
        )

    def process(self, data):
        for channel in data:
            for name, condition in self._conditions.items():
                if condition(data):
                    self._action(self._action_parameters, name, data)
