from typing import List

import numpy

from models.data.processing.epoching.epocher import Epocher
import mne as mne


class TrialWiseEpocher(Epocher):

    def __init__(self, samples_before: int = 0, samples_after: int = 0) -> None:
        super().__init__('Trial')
        if samples_before is None:
            raise ValueError('epoching.trial.wise.epocher.must.have.samples_before')
        if samples_after is None:
            raise ValueError('epoching.trial.wise.epocher.must.have.samples_after')

    @classmethod
    def from_config_json(cls, parameters: dict):
        if 'parameters' not in parameters:
            raise Exception('epoching.trial.wise.epocher.parameters.must.have.parameters')
        if 'samples-before' not in parameters['parameters']:
            raise Exception('epoching.trial.wise.epocher.parameters.must.have.samples-before')
        if 'samples-after' not in parameters['parameters']:
            raise Exception('epoching.trial.wise.epocher.parameters.must.have.samples-after')
        return cls(
            samples_before=parameters['parameters']['samples-before'],
            samples_after=parameters['parameters']['samples-after']
        )

    def process(self, data, label):
        marker_data: List = data[label]
        eeg_data: List = data[::label]
        timestamp_data: List = data[label + 1]
        marker_indexes = numpy.where(marker_data > 0)
        times: List = timestamp_data[marker_indexes]
        y = marker_data[marker_indexes]
        epochs = [

        ]
