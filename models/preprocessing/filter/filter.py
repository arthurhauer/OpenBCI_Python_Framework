from abc import ABC

from brainflow import FilterTypes

from config.configuration import Configuration
from models.preprocessing.node import PreProcessingNode


class Filter(PreProcessingNode):
    _filter: FilterTypes
    _sampling_rate: int
    _ripple: float
    _order: int

    def __init__(self, type: str, filter: str, order: int, sampling_frequency: int, ripple=None) -> None:
        super().__init__({'type': type})
        if type is None:
            raise Exception('preprocessing.node.invalid.parameters.must.have.type')
        self._type = type
        if filter is None:
            raise ValueError('preprocessing.filter.invalid.parameters.must.have.filter')
        elif filter not in ['BESSEL', 'BUTTERWORTH', 'CHEBYSHEV_TYPE_1']:
            raise ValueError('preprocessing.filter.invalid.parameters.filter.unsupported')
        if order is None:
            raise ValueError('preprocessing.filter.invalid.parameters.must.have.order')
        if order <= 0:
            raise ValueError('preprocessing.filter.invalid.parameters.order.must.be.greater.than.zero')
        if sampling_frequency <= 0:
            raise ValueError('preprocessing.filter.invalid.parameters.sampling.frequency.must.be.greater.than.zero')
        self._filter = FilterTypes[filter]
        self._sampling_rate = Configuration.get_sampling_frequency()
        self._order = order
        if self._filter == FilterTypes.CHEBYSHEV_TYPE_1:
            if ripple is None:
                raise ValueError('preprocessing.filter.invalid.parameters.must.have.ripple')
            else:
                self._ripple = ripple

    @classmethod
    def from_config_json(cls, parameters: dict):
        if 'type' not in parameters:
            raise Exception('preprocessing.node.invalid.parameters.must.have.type')
        if 'filter' not in parameters:
            raise ValueError('preprocessing.filter.invalid.parameters.must.have.filter')
        elif parameters['filter'] not in ['BESSEL', 'BUTTERWORTH', 'CHEBYSHEV_TYPE_1']:
            raise ValueError('preprocessing.filter.invalid.parameters.filter.unsupported')
        if 'order' not in parameters:
            raise ValueError('preprocessing.filter.invalid.parameters.must.have.order')
        if 'sampling-frequency' not in parameters:
            raise ValueError('preprocessing.filter.invalid.parameters.must.have.sampling.frequency')
        return cls(
            type=parameters['type'],
            filter=parameters['filter'],
            sampling_frequency=parameters['sampling-frequency'],
            order=parameters['order'],
            ripple=parameters['ripple']
        )
