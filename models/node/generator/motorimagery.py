import random
import time
from threading import Thread
from typing import List, Dict, Final

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.generator.generator_node import GeneratorNode
from models.utils.trial import Trial


class MotorImagery(GeneratorNode):
    """This node generates data for motor imagery. It generates data for a specific number of trials, and then it stops
    generating data. The trials are defined by the user in the configuration file. The node generates data for each
    trial in the order that they are defined in the configuration file. When the node finishes generating data for all
    the trials, it can either stop generating data or it can shuffle the trials and start generating data again.

    ``configuration.json`` usage:

        **module** (*str*): Current module name (in this case ``models.node.generator``).\n
        **type** (*str*): Current node type (in this case ``MotorImagery``).\n
        **trials** (*List[Trial]*): List of trials. A trial represents a specific event that you want to generate data for
        (e.g. Hand Grasp, Feet Movement, etc.). Each trial is defined by a dictionary containing the following parameters: \n
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
        **buffer_options** (*dict*): Buffer options.\n
            **clear_output_buffer_on_generate** (*bool*): If ``True``, the output buffer will be cleared when the node is executed.\n
        **shuffle_when_sequence_is_finished** (*bool*): If ``True``, the node will shuffle the trials when it finishes generating data for all the trials.\n

    """
    _MODULE_NAME: Final[str] = 'node.generator.motorimagery'

    OUTPUT_MARKER: Final[str] = 'marker'
    OUTPUT_TIMESTAMP: Final[str] = 'timestamp'

    def _validate_parameters(self, parameters: dict):
        """Validates the parameters that were passed to the node.

        :param parameters: The parameters that were passed to the node. this comes from the configuration file.
        :type parameters: dict

        :raises MissingParameterError: The ``Trial`` list is required.
        :raises MissingParameterError: The ``shuffle_when_sequence_is_finished`` parameter is required.
        """
        super()._validate_parameters(parameters)
        if 'trials' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='trials')
        if 'shuffle_when_sequence_is_finished' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='shuffle_when_sequence_is_finished')
        if 'max_sequence_runs' in parameters:
            if type(parameters['max_sequence_runs']) is not int:
                raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                            parameter='max_sequence_runs',
                                            cause='must_be_int')
            if parameters['max_sequence_runs'] <= 0:
                raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                            parameter='max_sequence_runs',
                                            cause='must_be_greater_than_0')

    def _initialize_parameter_fields(self, parameters: dict):
        """Initializes the parameter fields of the node.
        """
        super()._initialize_parameter_fields(parameters)
        self.trials = parameters['trials']
        self._trial_limit = len(self.trials) - 1
        self._trial_to_call = 0
        self.shuffle_when_sequence_is_finished = parameters['shuffle_when_sequence_is_finished']
        self._thread = Thread(target=self._execute_trial)
        self._has_max_sequence_runs = 'max_sequence_runs' in parameters
        if self._has_max_sequence_runs:
            self._max_sequence_runs = parameters['max_sequence_runs']
            self._sequence_runs_counter = 0
        self._stop_execution = False
        self._thread_started = False

    @classmethod
    def from_config_json(cls, parameters: dict):
        """Creates a new instance of this class and initializes it with the parameters that were passed to it.

        :param parameters: The parameters that will be passed to the node. This comes from the configuration file.
        :type parameters: dict

        :raises MissingParameterError: The ``Trial`` list is required.

        :return: A new instance of this class.
        """
        if 'name' not in parameters:
            raise MissingParameterError(module=cls._MODULE_NAME,
                                        parameter='name',
                                        name='undefined')
        name = parameters['name']
        if 'trials' not in parameters:
            raise MissingParameterError(module=cls._MODULE_NAME,
                                        parameter='trials',
                                        name=name)
        trials = []
        for trial_parameters in parameters['trials']:
            trial_parameters['name'] = name
            trials.append(Trial.from_config_json(trial_parameters))
        parameters['trials'] = trials
        return cls(parameters=parameters)

    def _is_next_node_call_enabled(self) -> bool:
        """Returns ``True`` if the node can call the next node in the pipeline, ``False`` otherwise."""
        return self._output_buffer[self.OUTPUT_TIMESTAMP].has_data()

    def _is_generate_data_condition_satisfied(self) -> bool:
        return True

    def _generate_data(self) -> Dict[str, FrameworkData]:
        """Generates data for the next trial. This method is called by the node when it is executed.
        """
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
        """Node self implementation of disposal of allocated resources.
        """
        self._clear_output_buffer()
        self._clear_input_buffer()
        self.stop()

    def start(self):
        """Starts the ``Trial`` execution using a thread.
        """
        self._thread_started = True
        self._stop_execution = False
        self._thread.start()

    def stop(self):
        """Stops the ``Trial`` execution.
        """
        if self._thread_started:
            self._thread_started = False
            self._stop_execution = True
            self._thread.join(1000)

    def _on_change_sequence(self):
        """Shuffle the generated data if necessary when the node finishes generating data for all the trials.
        """
        if self._has_max_sequence_runs:
            self._sequence_runs_counter += 1
            if self._sequence_runs_counter >= self._max_sequence_runs:
                raise Exception(f'{self._MODULE_NAME}.{self.name} Max sequence runs reached. Stopping Execution.')

        if self.shuffle_when_sequence_is_finished:
            random.shuffle(self.trials)

    def _next_trial(self):
        self._trial_to_call += 1
        if self._trial_to_call > self._trial_limit:
            self._trial_to_call = 0
            self._on_change_sequence()
        self._execute_trial()

    def _execute_trial(self):
        """This method is responsible for executing the current trial and calling the next trial when the current trial
        finishes.
        """
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
