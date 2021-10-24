from brainflow import DataFilter

from models.preprocessing.filter.filter import Filter


class CutOffFilter(Filter):
    _cutoff_freq: float

    def __init__(self, parameters: dict) -> None:
        super(Filter).__init__(parameters)
        self._cutoff_freq = parameters['cutoff_freq']

        if super()._type == 'LOWPASS':
            self._set_lowpass()
        elif super()._type == 'HIGHPASS':
            self._set_highpass()
        else:
            raise ValueError("Invalid cutoff filter type " + super()._type)

    def _set_lowpass(self):
        super()._action = lambda data: DataFilter.perform_lowpass(data,
                                                                  self._sampling_rate,
                                                                  self._cutoff_freq,
                                                                  self._order,
                                                                  self._filter,
                                                                  self._ripple)

    def _set_highpass(self):
        super()._action = lambda data: DataFilter.perform_highpass(data,
                                                                   self._sampling_rate,
                                                                   self._cutoff_freq,
                                                                   self._order,
                                                                   self._filter,
                                                                   self._ripple)

