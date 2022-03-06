import multiprocessing
import random
from threading import Thread
from typing import List

from models.session.trial import Trial


class Session:
    def __init__(self, trials: List[Trial],
                 feature_extractor_training_repetitions: int = 0,
                 classifier_training_repetitions: int = 0,
                 test_repetitions: int = 1,
                 randomize: bool = False,
                 on_stop=None,
                 on_change_sequence=None,
                 on_feature_extractor_training_end=None,
                 on_classifier_training_end=None) -> None:
        super().__init__()
        if trials is None:
            raise ValueError('trial.must.have.trials')
        if feature_extractor_training_repetitions is None:
            raise ValueError('trial.must.have.repetitions')
        if classifier_training_repetitions is None:
            raise ValueError('trial.must.have.repetitions')
        if test_repetitions is None:
            raise ValueError('trial.must.have.repetitions')
        if on_stop is None:
            on_stop = self.on_stop
        if on_change_sequence is None:
            on_change_sequence = self.on_change_trial
        if on_feature_extractor_training_end is None:
            on_feature_extractor_training_end = self.on_feature_extractor_training_end
        if on_classifier_training_end is None:
            on_classifier_training_end = self.on_classifier_training_end

        self.trials = trials

        self.feature_extractor_training_repetitions = feature_extractor_training_repetitions
        self.classifier_training_repetitions = classifier_training_repetitions
        self.test_repetitions = test_repetitions
        self.repetitions = self.feature_extractor_training_repetitions + self.classifier_training_repetitions + self.test_repetitions
        if self.repetitions <= 0:
            raise ValueError('trial.repetitions.must.be.greater.than.zero')

        self.on_stop = on_stop
        self.on_change_sequence = on_change_sequence
        self.randomize = randomize
        if self.randomize:
            self._shuffle_trials()
        self._trial_limit = len(self.trials) - 1
        self._trial_to_call = 0
        self._current_sequence = self.trials[self._trial_to_call]

        self._current_repetition = 0
        self._thread = Thread(target=self._execute_trial)

    @classmethod
    def from_config_json(cls, parameters: dict):
        if 'repetitions' not in parameters:
            raise ValueError('session.must.have.repetitions')
        if 'feature-extractor-training' not in parameters['repetitions']:
            raise ValueError('session.repetitions.must.have.feature-extractor-training')
        if 'classifier-training' not in parameters['repetitions']:
            raise ValueError('session.repetitions.must.have.classifier-training')
        if 'test' not in parameters['repetitions']:
            raise ValueError('session.repetitions.must.have.test')
        if 'trials' not in parameters:
            raise ValueError('session.must.have.trials')
        if 'randomize' not in parameters:
            randomize = False
        else:
            randomize = parameters['randomize']
        trials = []
        for trial_parameters in parameters['trials']:
            trials.append(Trial.from_config_json(trial_parameters))
        return cls(
            trials=trials,
            feature_extractor_training_repetitions=parameters['repetitions']['feature-extractor-training'],
            classifier_training_repetitions=parameters['repetitions']['classifier-training'],
            test_repetitions=parameters['repetitions']['test'],
            randomize=randomize
        )

    def _shuffle_trials(self):
        random.shuffle(self.trials)

    def get_current_trial_code(self) -> int:
        return self.trials[self._trial_to_call].code

    def start(self):
        if self._current_repetition == self.feature_extractor_training_repetitions:
            self.on_feature_extractor_training_end()
        if self._current_repetition == (
                self.feature_extractor_training_repetitions + self.classifier_training_repetitions):
            self.on_classifier_training_end()
        self._thread.start()

    def on_stop(self):
        pass

    def on_change_trial(self, sequence_index):
        pass

    def on_feature_extractor_training_end(self):
        pass

    def on_classifier_training_end(self):
        pass

    def _next_trial(self):
        self._trial_to_call += 1
        if self._trial_to_call > self._trial_limit:
            self._trial_to_call = 0
            self._shuffle_trials()
            self._current_repetition += 1
            if self._current_repetition == self.feature_extractor_training_repetitions:
                self.on_feature_extractor_training_end()
            if self._current_repetition == (
                    self.feature_extractor_training_repetitions + self.classifier_training_repetitions):
                self.on_classifier_training_end()
            if self._current_repetition > self.repetitions:
                self.on_stop()
                self._thread.join()
                return
        self.on_change_sequence(self._trial_to_call)
        self._execute_trial()

    def _execute_trial(self):
        trial = self.trials[self._trial_to_call]
        trial.on_stop = self._next_trial
        trial.start()
