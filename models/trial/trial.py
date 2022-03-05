import multiprocessing
from threading import Thread
from typing import List

from models.trial.sequence import Sequence


class Trial:
    def __init__(self, sequence: List[Sequence], repetitions: int = 1, on_stop=None, on_change_sequence=None) -> None:
        super().__init__()
        if sequence is None:
            raise ValueError('trial.must.have.sequence')
        if repetitions is None:
            raise ValueError('trial.must.have.repetitions')
        if repetitions <= 0:
            raise ValueError('trial.repetitions.must.be.greater.than.zero')
        if on_stop is None:
            on_stop = self.on_stop
        if on_change_sequence is None:
            on_change_sequence = self.on_change_sequence

        self.sequence = sequence
        self.repetitions = repetitions
        self.on_stop = on_stop
        self.on_change_sequence = on_change_sequence
        self._sequence_to_call = 0
        self._sequence_limit = len(self.sequence) - 1
        self._current_repetition = 1
        self._thread = Thread(target=self._execute_sequence)

    @classmethod
    def from_config_json(cls, parameters: dict):
        if 'repetitions' not in parameters:
            raise ValueError('trial.must.have.repetitions')
        if 'sequence' not in parameters:
            raise ValueError('trial.must.have.sequence')
        sequence = []
        for sequence_parameters in parameters['sequence']:
            sequence.append(Sequence.from_config_json(sequence_parameters))
        return cls(
            sequence=sequence,
            repetitions=parameters['repetitions']
        )

    def get_current_sequence(self):
        return self._sequence_to_call

    def start(self):
        self._thread.start()

    def on_stop(self):
        pass

    def on_change_sequence(self, sequence_index):
        pass

    def _next_sequence(self):
        self._sequence_to_call += 1
        if self._sequence_to_call > self._sequence_limit:
            self._current_repetition += 1
            self._sequence_to_call = 0
            if self._current_repetition > self.repetitions:
                self.on_stop()
                self._thread.join()
                return
        self.on_change_sequence(self._sequence_to_call)
        self._execute_sequence()

    def _execute_sequence(self):
        sequence = self.sequence[self._sequence_to_call]
        sequence.on_stop = self._next_sequence
        sequence.start()
