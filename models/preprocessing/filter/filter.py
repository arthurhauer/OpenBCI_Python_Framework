from abc import ABC

from brainflow import FilterTypes

from config.configuration import Configuration
from models.preprocessing.node import PreProcessingNode


class Filter(PreProcessingNode):
    _filter: FilterTypes
    _sampling_rate: int
    _ripple: float
    _order: int

    def __init__(self, parameters: dict) -> None:
        super().__init__(parameters)
        if 'type' not in parameters:
            raise Exception('preprocessing.node.invalid.parameters.must.have.type')
        self._type = parameters['type']
        if 'filter' not in parameters:
            raise ValueError('preprocessing.filter.invalid.parameters.must.have.filter')
        elif parameters['filter'] not in ['BESSEL', 'BUTTERWORTH', 'CHEBYSHEV_TYPE_1']:
            raise ValueError('preprocessing.filter.invalid.parameters.filter.unsupported')
        if 'order' not in parameters:
            raise ValueError('preprocessing.filter.invalid.parameters.must.have.order')
        self._filter = FilterTypes[parameters['filter']]
        self._sampling_rate = Configuration.get_sampling_frequency()
        self._order = parameters['order']
        if self._filter == FilterTypes.CHEBYSHEV_TYPE_1:
            if 'ripple' not in parameters:
                raise ValueError('preprocessing.filter.invalid.parameters.must.have.ripple')
            else:
                self._ripple = parameters['ripple']
        else:
            self._ripple = 0.0
