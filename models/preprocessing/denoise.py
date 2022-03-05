from typing import List

from brainflow import DataFilter, DetrendOperations, NoiseTypes

from models.preprocessing.node import PreProcessingNode


class Denoise(PreProcessingNode):
    __allowed_wavelets = None

    def __init__(self, type: str,
                 noise_type: str = None,
                 sampling_frequency: int = None,
                 wavelet: str = None,
                 decomposition_level: int = None) -> None:
        super().__init__()
        if type is None:
            raise ValueError('preprocessing.denoise.invalid.parameters.must.have.type')
        if type not in ['ENVIRONMENT', 'WAVELET']:
            raise ValueError('preprocessing.denoise.invalid.parameters.unsupported.type')
        if type == 'ENVIRONMENT':
            if noise_type is None:
                raise ValueError('preprocessing.denoise.invalid.parameters.must.have.noise.type')
            if noise_type not in ['FIFTY', 'SIXTY', 'EACH']:
                raise ValueError('preprocessing.denoise.invalid.parameters.unsupported.noise.type')
            if sampling_frequency is None:
                raise ValueError('preprocessing.denoise.invalid.parameters.must.have.sampling.frequency')
            if sampling_frequency <= 0:
                raise ValueError(
                    'preprocessing.denoise.invalid.parameters.sampling.frequency.must.be.greater.than.zero')
            self._noise_type = NoiseTypes[noise_type]
            self._sampling_frequency = sampling_frequency
            self._denoise_process = self._set_environment

        elif type == 'WAVELET':
            if wavelet is None:
                raise ValueError('preprocessing.denoise.invalid.parameters.must.have.noise.type')
            if wavelet not in self._allowed_wavelets:
                raise ValueError('preprocessing.denoise.invalid.parameters.unsupported.wavelet')
            if decomposition_level is None:
                raise ValueError('preprocessing.denoise.invalid.parameters.must.have.decomposition.level')
            if decomposition_level <= 0:
                raise ValueError(
                    'preprocessing.denoise.invalid.parameters.decomposition.level.must.be.greater.than.zero')
            self._wavelet_type = wavelet
            self._decomposition_level = decomposition_level
            self._denoise_process = self._set_wavelet

    @classmethod
    def from_config_json(cls, parameters: dict):
        if 'type' not in parameters:
            raise Exception('preprocessing.denoise.invalid.parameters.must.have.type')
        if 'parameters' not in parameters:
            raise Exception('preprocessing.denoise.invalid.parameters.must.have.parameters')
        if parameters['type'] == 'ENVIRONMENT':
            if 'noise-type' not in parameters['parameters']:
                raise ValueError('preprocessing.denoise.invalid.parameters.must.have.noise-type')
            if 'sampling-frequency' not in parameters:
                raise ValueError('preprocessing.denoise.invalid.parameters.must.have.sampling-frequency')
            return cls(
                type=parameters['type'],
                noise_type=parameters['parameters']['noise-type'],
                sampling_frequency=parameters['sampling-frequency']
            )
        elif parameters['type'] == 'WAVELET':
            if 'wavelet' not in parameters['parameters']:
                raise ValueError('preprocessing.denoise.invalid.parameters.must.have.wavelet')
            if 'decomposition-level' not in parameters['parameters']:
                raise ValueError('preprocessing.denoise.invalid.parameters.must.have.decomposition-level')
            return cls(
                type=parameters['type'],
                wavelet=parameters['parameters']['wavelet'],
                decomposition_level=parameters['parameters']['decomposition-level']
            )
        else:
            raise ValueError('preprocessing.denoise.invalid.parameters.unsupported.type')

    @property
    def _allowed_wavelets(self):
        if Denoise.__allowed_wavelets is None:
            allowed_wavelets = ['haar',
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
            allowed_wavelets.extend(['db%d' % index for index in range(1, 16)])
            allowed_wavelets.extend(['sym%d' % index for index in range(2, 11)])
            allowed_wavelets.extend(['coif%d' % index for index in range(1, 6)])
            Denoise.__allowed_wavelets = allowed_wavelets
        return Denoise.__allowed_wavelets

    def _set_environment(self, data):
        DataFilter.remove_environmental_noise(data, self._sampling_frequency, self._noise_type)

    def _set_wavelet(self, data):
        DataFilter.perform_wavelet_denoising(data, self._wavelet_type, self._decomposition_level)

    def process(self, data):
        for channel in data:
            self._denoise_process(data)
