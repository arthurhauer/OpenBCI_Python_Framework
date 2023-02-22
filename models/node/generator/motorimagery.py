import random
import time
from threading import Thread
from typing import List, Dict, Final

from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.generator.generator_node import GeneratorNode
from models.utils.trial import Trial


class MotorImagery(GeneratorNode):
    _MODULE_NAME: Final[str] = 'node.generator.motorimagery'

    OUTPUT_MARKER: Final[str] = 'marker'
    OUTPUT_TIMESTAMP: Final[str] = 'timestamp'

    def _validate_parameters(self, parameters: dict):
        super()._validate_parameters(parameters)
        if 'trials' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME,name=self.name,
                                        parameter='trials')
        if 'shuffle_when_sequence_is_finished' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME,name=self.name,
                                        parameter='shuffle_when_sequence_is_finished')

    def _initialize_parameter_fields(self, parameters: dict):
        super()._initialize_parameter_fields(parameters)
        self.trials = parameters['trials']
        self._trial_limit = len(self.trials) - 1
        self._trial_to_call = 0
        self.shuffle_when_sequence_is_finished = parameters['shuffle_when_sequence_is_finished']
        self._thread = Thread(target=self._execute_trial)
        self._stop_execution = False
        self._thread_started = False

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
        return self._output_buffer[self.OUTPUT_TIMESTAMP].has_data()

    def _is_generate_data_condition_satisfied(self) -> bool:
        return True

    def _generate_data(self) -> Dict[str, FrameworkData]:
        if not self._thread_started:
            self.start()
        return_value = self._input_buffer.copy()
        self._clear_input_buffer()
        return return_value

    def _get_inputs(self) -> List[str]:
        return self._get_outputs()

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
        self._thread_started = True
        self._stop_execution = False
        self._thread.start()

    def stop(self):
        if self._thread_started:
            self._thread_started = False
            self._stop_execution = True
            self._thread.join(1000)

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
        if self._stop_execution:
            return
        trial.on_stop = self._next_trial

        # Set sampling frequency to 1 as this generator node doesn't have a fixed generation rate,
        # being completely dependent on user configuration for each trial
        marker_data = FrameworkData.from_single_channel(1, [trial.code])
        timestamp_data = FrameworkData.from_single_channel(1, [time.time()])

        self._insert_new_input_data(marker_data, self.OUTPUT_MARKER)
        self._insert_new_input_data(timestamp_data, self.OUTPUT_TIMESTAMP)

        trial.start()
