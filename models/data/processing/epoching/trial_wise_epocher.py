from typing import List

import numpy

from models.data.processing.epoching.epocher import Epocher


class TrialWiseEpocher(Epocher):

    def __init__(self, sampling_frequency: int, trial_length: int, samples_before: int = 0,
                 samples_after: int = 0) -> None:
        super().__init__('Trial', sampling_frequency, trial_length)
        if samples_before is None:
            raise ValueError('epoching.trial.wise.epocher.must.have.samples_before')
        if samples_before < 0:
            raise ValueError('epoching.trial.wise.epocher.samples_before.must.be.greater.than.or.equal.to.zero')
        if samples_after is None:
            raise ValueError('epoching.trial.wise.epocher.must.have.samples_after')
        if samples_after < 0:
            raise ValueError('epoching.trial.wise.epocher.samples_after.must.be.greater.than.or.equal.to.zero')
        self.samples_before = samples_before
        self.samples_after = samples_after

    @classmethod
    def from_config_json(cls, parameters: dict):
        if 'samples-before' not in parameters:
            raise Exception('epoching.trial.wise.epocher.parameters.must.have.samples-before')
        if 'samples-after' not in parameters:
            raise Exception('epoching.trial.wise.epocher.parameters.must.have.samples-after')
        if 'trial-length' not in parameters:
            raise Exception('epoching.trial.wise.epocher.parameters.must.have.trial-length')
        return cls(
            samples_before=parameters['samples-before'],
            samples_after=parameters['samples-after'],
            sampling_frequency=parameters['sampling-frequency'],
            trial_length=parameters['trial-length']
        )

    def process(self, data, label):
        marker_data: List = data[label]
        eeg_data: List = data[0:label]
        timestamp_data: List = data[label + 1]
        marker_indexes = numpy.where(marker_data > 0)
        if len(marker_indexes[0]) == 0:
            treated_epochs = [
                eeg_data
            ]
            return numpy.array(treated_epochs), []
        else:
            marker_events = numpy.array(marker_data[marker_indexes])
            epochs = []
            last_marker_index = 0
            for index in marker_indexes[0]:
                # crop samples after start and before end of trial
                start_index = last_marker_index + self.samples_after
                end_index = index - self.samples_before
                raw_data = eeg_data[0:label, start_index:end_index]

                # get fixed size epochs
                epochs.append(raw_data[:, -self.trial_length::])

                last_marker_index = index

            return numpy.array(epochs), marker_events
