from abc import ABC

from brainflow import FilterTypes

from models.preprocessing.processor import Processor


class Filter(Processor):
    _filter: FilterTypes
    _sampling_rate: int
    _ripple: float
    _order: int

    def __init__(self, parameters: dict) -> None:
        super(Processor).__init__(parameters)
        if parameters['filter'] is None:
            raise Exception('preprocessing.filter.invalid.parameters.must.have.filter')
        if parameters['sampling_rate'] is None:
            raise Exception('preprocessing.filter.invalid.parameters.must.have.sampling_rate')
        if parameters['order'] is None:
            raise Exception('preprocessing.filter.invalid.parameters.must.have.order')
        self._filter = FilterTypes[parameters['filter']]
        self._sampling_rate = parameters['sampling_rate']
        self._order = parameters['order']
        if parameters['ripple'] is None and self._filter == FilterTypes.CHEBYSHEV_TYPE_1:
            raise Exception('preprocessing.filter.invalid.parameters.must.have.ripple')
        self._ripple = parameters['ripple']
