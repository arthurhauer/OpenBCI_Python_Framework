from brainflow import DataFilter

from models.preprocessing.filter.filter import Filter


class CutOffFilter(Filter):
    _cutoff_freq: float

    def __init__(self, parameters: dict) -> None:
        super().__init__(parameters)
        if 'cutoff-freq' not in parameters:
            raise ValueError('preprocessing.filter.bandfilter.invalid.parameters.must.have.cutoff-freq')
        self._cutoff_freq = parameters['cutoff-freq']
        if self._type == 'LOWPASS':
            self.process = self._set_lowpass
        elif self._type == 'HIGHPASS':
            self.process = self._set_highpass
        else:
            raise ValueError("Invalid cutoff filter type " + self._type)

    def _set_lowpass(self, data):
        DataFilter.perform_lowpass(data,
                                   self._sampling_rate,
                                   self._cutoff_freq,
                                   self._order,
                                   self._filter,
                                   self._ripple)

    def _set_highpass(self, data):
        DataFilter.perform_highpass(data,
                                    self._sampling_rate,
                                    self._cutoff_freq,
                                    self._order,
                                    self._filter,
                                    self._ripple)
