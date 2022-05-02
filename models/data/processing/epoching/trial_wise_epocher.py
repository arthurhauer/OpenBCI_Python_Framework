from typing import List

import numpy

from models.data.processing.epoching.epocher import Epocher


class TrialWiseEpocher(Epocher):

    def __init__(self, sampling_frequency: int, samples_before: int = 0, samples_after: int = 0) -> None:
        super().__init__('Trial', sampling_frequency)
        if samples_before is None:
            raise ValueError('epoching.trial.wise.epocher.must.have.samples_before')
        if samples_after is None:
            raise ValueError('epoching.trial.wise.epocher.must.have.samples_after')

    @classmethod
    def from_config_json(cls, parameters: dict):
        if 'samples-before' not in parameters:
            raise Exception('epoching.trial.wise.epocher.parameters.must.have.samples-before')
        if 'samples-after' not in parameters:
            raise Exception('epoching.trial.wise.epocher.parameters.must.have.samples-after')
        return cls(
            samples_before=parameters['samples-before'],
            samples_after=parameters['samples-after'],
            sampling_frequency=parameters['sampling-frequency']
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
            min_sample_size = None
            for index in marker_indexes[0]:
                new_data = eeg_data[0:label, last_marker_index:index]
                epochs.append(new_data)
                if min_sample_size is None or min_sample_size > (index - last_marker_index):
                    min_sample_size = index - last_marker_index
                last_marker_index = index

            treated_epochs = []
            for epoch in epochs:
                treated_epochs.append(epoch[:, 0:min_sample_size - 1])

            return numpy.array(treated_epochs), marker_events
