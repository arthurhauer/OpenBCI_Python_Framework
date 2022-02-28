import os.path

import numpy as np

from globals.globals import SIGNAL_CHECK_ACTION_DIR
from models.preprocessing.node import PreProcessingNode


class SignalCheck(PreProcessingNode):

    def __init__(self, action, action_parameters: dict, conditions: list) -> None:
        super().__init__({})
        self._action = action
        self._action_parameters = action_parameters
        self._conditions = conditions

    @classmethod
    def from_predefined_conditions(cls, action, action_parameters, power_grid_frequency: float, min_amplitude: float,
                                   min_rms: float):
        # TODO Include powergrid frequency check
        cls.__init__(
            action=action,
            action_parameters=action_parameters,
            conditions=[
                lambda data: (max(data) - min(data)) < min_amplitude,
                lambda data: (np.sqrt(np.mean(data ** 2))) < min_rms
            ]
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
        if not os.path.isfile(action_path):
            raise ValueError(
                'preprocessing.signal.check.invalid.parameters.action.file.doesnt.exist.' + parameters['action'])
        # Setting instance attribute so the compiler won't complain
        custom_action = None
        # Open and read the given custom python script
        file = open(action_path, 'r')
        script = file.read()
        # Force instance attribute reference to user script-defined function
        script += '\ncustom_action = action'
        # Compile the script
        compiled_script = compile(script, '', 'exec')
        # Execute the script, setting self._action
        exec(compiled_script)
        action_parameters = {
            key: parameters['action']['parameters'][key] for key in parameters['action']['parameters']
        }
        cls.from_predefined_conditions(
            cls,
            action=custom_action,
            action_parameters=action_parameters,
            power_grid_frequency=parameters['power-grid-frequency'],
            min_amplitude=parameters['min-amplitude'],
            min_rms=parameters['min-rms']
        )

    def process(self, data):
        for condition in self._conditions:
            if condition(data):
                self._action(self._action_parameters, data)
