import random
from multiprocessing import Process
from typing import List, Dict, Final

from models.exception.missing_parameter import MissingParameterError
from models.node.generator.generator_node import GeneratorNode
from models.utils.trial import Trial


class MotorImagery(GeneratorNode):
    _MODULE_NAME: Final[str] = 'node.generator.motorimagery'

    OUTPUT_MARKER: Final[str] = 'marker'
    OUTPUT_TIMESTAMP: Final[str] = 'timestamp'

    def __init__(self, parameters: dict) -> None:
        super().__init__(parameters)

        if 'trials' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME,
                                        parameter='trials')
        if 'shuffle_when_sequence_is_finished' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME,
                                        parameter='shuffle_when_sequence_is_finished')
        self.trials = parameters['trials']
        self._trial_limit = len(self.trials) - 1
        self._trial_to_call = 0
        self.shuffle_when_sequence_is_finished = parameters['shuffle_when_sequence_is_finished']
        self._process = Process(target=self._execute_trial)

    @classmethod
    def from_config_json(cls, parameters: dict):
        if 'trials' not in parameters:
            raise MissingParameterError(module=cls._MODULE_NAME,
                                        parameter='trials')
        trials = []
        for trial_parameters in parameters['trials']:
            trials.append(Trial.from_config_json(trial_parameters))
        parameters['trials'] = trials
        return cls(parameters=parameters)

    def _is_next_node_call_enabled(self) -> bool:
        return True

    def _is_generate_data_condition_satisfied(self) -> bool:
        return True

    def _generate_data(self) -> Dict[str, list]:
        pass

    def _get_outputs(self) -> List[str]:
        return [
            self.OUTPUT_MARKER,
            self.OUTPUT_TIMESTAMP
        ]

    def dispose(self) -> None:
        self._clear_output_buffer()
        self._clear_input_buffer()
        self.stop()

    def start(self):
        self._process.start()

    def stop(self):
        self._process.terminate()

    def _on_change_sequence(self):
        if self.shuffle_when_sequence_is_finished:
            random.shuffle(self.trials)

    def _next_trial(self):
        self._trial_to_call += 1
        if self._trial_to_call > self._trial_limit:
            self._trial_to_call = 0
            self._on_change_sequence()
        self._execute_trial()

    def _execute_trial(self):
        trial = self.trials[self._trial_to_call]
        trial.on_stop = self._next_trial
        self.on_change_trial(trial.code)
        trial.start()
