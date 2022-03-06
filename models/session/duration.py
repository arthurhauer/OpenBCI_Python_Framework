from scipy import stats


class Duration:
    def __init__(self, mean: float, standard_deviation: float, maximum: float, minimum: float) -> None:
        super().__init__()
        if mean is None:
            raise ValueError('trial.sequence.duration.must.have.mean')
        if standard_deviation is None:
            raise ValueError('trial.sequence.duration.must.have.standard.deviation')
        if maximum is None:
            raise ValueError('trial.sequence.duration.must.have.maximum')
        if minimum is None:
            raise ValueError('trial.sequence.duration.must.have.minimum')
        if mean <= 0:
            raise ValueError('trial.sequence.duration.mean.must.be.greater.than.zero')
        if standard_deviation <= 0:
            raise ValueError('trial.sequence.duration.standard.deviation.must.be.greater.than.zero')
        if maximum <= 0:
            raise ValueError('trial.sequence.duration.maximum.must.be.greater.than.zero')
        if maximum < mean:
            raise ValueError('trial.sequence.duration.mean.must.be.greater.than.mean')
        if minimum <= 0:
            raise ValueError('trial.sequence.duration.mean.must.be.greater.than.zero')
        if minimum > mean:
            raise ValueError('trial.sequence.duration.mean.must.be.lesser.than.mean')
        self.mean = mean
        self.standard_deviation = standard_deviation
        self.maximum = maximum
        self.minimum = minimum
        self._distribution = stats.truncnorm((self.minimum - self.mean) / self.standard_deviation,
                                             (self.maximum - self.mean) / self.standard_deviation, loc=self.mean,
                                             scale=self.standard_deviation)

    @classmethod
    def from_config_json(cls, parameters: dict):
        if 'mean' not in parameters:
            raise ValueError('trial.sequence.duration.must.have.mean')
        if 'standard-deviation' not in parameters:
            raise ValueError('trial.sequence.duration.must.have.standard-deviation')
        if 'maximum' not in parameters:
            raise ValueError('trial.sequence.duration.must.have.maximum')
        if 'minimum' not in parameters:
            raise ValueError('trial.sequence.duration.must.have.minimum')
        return cls(
            mean=parameters['mean'],
            standard_deviation=parameters['standard-deviation'],
            maximum=parameters['maximum'],
            minimum=parameters['minimum']
        )

    def get_duration(self) -> float:
        return self._distribution.rvs(1)[0]
