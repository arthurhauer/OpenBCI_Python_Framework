from brainflow import DataFilter

from models.preprocessing.filter.filter import Filter


class CutOffFilter(Filter):
    _cutoff_frequency: float

    def __init__(self, type: str, filter: str, order: int, sampling_frequency: int, cutoff_frequency: float,
                 ripple=None) -> None:
        super().__init__(
            type=type,
            filter=filter,
            order=order,
            sampling_frequency=sampling_frequency,
            ripple=ripple
        )
        if cutoff_frequency is None:
            raise ValueError('preprocessing.filter.bandfilter.invalid.parameters.must.have.cut-off.frequency')
        if cutoff_frequency <= 0:
            raise ValueError(
                'preprocessing.filter.bandfilter.invalid.parameters.cut-off.frequency.must.be.greater.than.zero')
        self._cutoff_frequency = cutoff_frequency
        if self._type == 'LOWPASS':
            self.filter_process = self._set_lowpass
        elif self._type == 'HIGHPASS':
            self.filter_process = self._set_highpass
        else:
            raise ValueError("Invalid cutoff filter type " + self._type)

    @classmethod
    def from_config_json(cls, parameters: dict):
        if 'cutoff-frequency' not in parameters:
            raise ValueError('preprocessing.filter.bandfilter.invalid.parameters.must.have.cutoff-frequency')
        return cls(
            type=parameters['type'],
            filter=parameters['filter'],
            sampling_frequency=parameters['sampling-frequency'],
            order=parameters['order'],
            ripple=parameters['ripple'],
            cutoff_frequency=parameters['cutoff-frequency']
        )

    def _set_lowpass(self, data):
        DataFilter.perform_lowpass(data,
                                   self._sampling_rate,
                                   self._cutoff_frequency,
                                   self._order,
                                   self._filter,
                                   self._ripple)

    def _set_highpass(self, data):
        DataFilter.perform_highpass(data,
                                    self._sampling_rate,
                                    self._cutoff_frequency,
                                    self._order,
                                    self._filter,
                                    self._ripple)

    def process(self, data):
        for channel in data:
            self.filter_process(data)
