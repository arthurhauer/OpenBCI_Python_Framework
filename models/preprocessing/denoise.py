from typing import List

from brainflow import DataFilter, DetrendOperations

from models.preprocessing.node import PreProcessingNode


class Denoise(PreProcessingNode):
    __allowed_types = None

    def __init__(self, type: str, decomposition_level: int) -> None:
        super().__init__()
        if type is None:
            raise ValueError('preprocessing.denoise.invalid.parameters.must.have.type')
        if decomposition_level is None:
            raise ValueError('preprocessing.denoise.invalid.parameters.must.have.decomposition.level')
        self._wavelet_type = type
        if self._wavelet_type not in self._allowed_types:
            raise ValueError('preprocessing.denoise.invalid.parameters.unsupported.type')
        if decomposition_level <= 0:
            raise ValueError('preprocessing.denoise.invalid.parameters.decomposition.level.must.be.greater.than.zero')
        self._decomposition_level=decomposition_level

    @classmethod
    def from_config_json(cls, parameters: dict):
        if 'type' not in parameters:
            raise Exception('preprocessing.denoise.invalid.parameters.must.have.type')
        if 'decomposition-level' not in parameters:
            raise Exception('preprocessing.denoise.invalid.parameters.must.have.decomposition-level')
        return cls(
            type=parameters['type'],
            decomposition_level=parameters['decomposition-level']
        )

    @property
    def _allowed_types(self):
        if Denoise.__allowed_types is None:
            allowed_types = ['haar',
                             'bior1.1',
                             'bior1.3',
                             'bior1.5',
                             'bior2.2',
                             'bior2.4',
                             'bior2.6',
                             'bior2.8',
                             'bior3.1',
                             'bior3.3',
                             'bior3.5',
                             'bior3.7',
                             'bior3.9',
                             'bior4.4',
                             'bior5.5',
                             'bior6.8']
            allowed_types.extend(['db%d' % index for index in range(1, 16)])
            allowed_types.extend(['sym%d' % index for index in range(2, 11)])
            allowed_types.extend(['coif%d' % index for index in range(1, 6)])
            Denoise.__allowed_types = allowed_types
        return Denoise.__allowed_types

    def process(self, data):
        DataFilter.perform_wavelet_denoising(data, self._wavelet_type, self._decomposition_level)
