from brainflow import DataFilter

from models.preprocessing.filter.filter import Filter


class BandFilter(Filter):
    _center_frequency: float
    _band_width: float

    def __init__(self, type: str,
                 filter: str,
                 order: int,
                 sampling_frequency: int,
                 center_frequency: float,
                 band_width: float,
                 ripple=None) -> None:

        super().__init__(
            type=type,
            filter=filter,
            order=order,
            sampling_frequency=sampling_frequency,
            ripple=ripple
        )
        if center_frequency is None:
            raise ValueError('preprocessing.filter.band.filter.invalid.parameters.must.have.center.frequency')
        if center_frequency <= 0:
            raise ValueError(
                'preprocessing.filter.band.filter.invalid.parameters.center.frequency.must.be.greater.than.zero')
        if band_width is None:
            raise ValueError('preprocessing.filter.band.filter.invalid.parameters.must.have.band.width')
        if band_width <= 0:
            raise ValueError('preprocessing.filter.band.filter.invalid.parameters.band.width.must.be.greater.than.zero')
        self._center_frequency = center_frequency
        self._band_width = band_width
        if self._type == 'BANDPASS':
            self.filter_process = self._set_bandpass
        elif self._type == 'BANDSTOP':
            self.filter_process = self._set_bandstop
        else:
            raise ValueError("Invalid band filter type " + super()._type)

    @classmethod
    def from_config_json(cls, parameters: dict):
        if 'center-frequency' not in parameters:
            raise ValueError('preprocessing.filter.band.filter.invalid.parameters.must.have.center-frequency')
        if 'band-width' not in parameters:
            raise ValueError('preprocessing.filter.band.filter.invalid.parameters.must.have.band-width')
        return cls(
            type=parameters['type'],
            filter=parameters['filter'],
            sampling_frequency=parameters['sampling-frequency'],
            order=parameters['order'],
            ripple=parameters['ripple'],
            center_frequency=parameters['center-frequency'],
            band_width=parameters['band-width']
        )

    def _set_bandpass(self, data):
        DataFilter.perform_bandpass(data,
                                    self._sampling_rate,
                                    self._center_frequency,
                                    self._band_width,
                                    self._order,
                                    self._filter,
                                    self._ripple)

    def _set_bandstop(self, data):
        DataFilter.perform_bandstop(data,
                                    self._sampling_rate,
                                    self._center_frequency,
                                    self._band_width,
                                    self._order,
                                    self._filter,
                                    self._ripple)

    def process(self, data):
        self.filter_process(data)
