from brainflow import DataFilter

from models.preprocessing.filter.filter import Filter


class BandFilter(Filter):
    _center_freq: float
    _band_width: float

    def __init__(self, parameters: dict) -> None:
        super().__init__(parameters)
        if 'center-freq' not in parameters:
            raise ValueError('preprocessing.filter.bandfilter.invalid.parameters.must.have.center-freq')
        self._center_freq = parameters['center-freq']
        if 'band-width' not in parameters:
            raise ValueError('preprocessing.filter.bandfilter.invalid.parameters.must.have.band-width')
        self._band_width = parameters['band-width']
        if self._type == 'BANDPASS':
            self._set_bandpass()
        elif self._type == 'BANDSTOP':
            self._set_bandstop()
        else:
            raise ValueError("Invalid band filter type " + super()._type)

    def _set_bandpass(self):
        self._action = lambda data: DataFilter.perform_bandpass(data,
                                                                self._sampling_rate,
                                                                self._center_freq,
                                                                self._band_width,
                                                                self._order,
                                                                self._filter,
                                                                self._ripple)

    def _set_bandstop(self):
        self._action = lambda data: DataFilter.perform_bandstop(data,
                                                                self._sampling_rate,
                                                                self._center_freq,
                                                                self._band_width,
                                                                self._order,
                                                                self._filter,
                                                                self._ripple)
