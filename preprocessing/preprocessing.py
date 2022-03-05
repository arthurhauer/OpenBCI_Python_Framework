from typing import List

from config.configuration import Configuration
from models.data.processing.preprocessing.custom import Custom
from models.data.processing.preprocessing.denoise import Denoise
from models.data.processing.preprocessing.detrend import Detrend
from models.data.processing.preprocessing.downsample import Downsample
from models.data.processing.preprocessing.filter.band_filter import BandFilter
from models.data.processing.preprocessing.filter.cutoff_filter import CutOffFilter
from models.data.processing.preprocessing.filter.filter import Filter
from models.data.processing.processing_node import ProcessingNode
from models.data.processing.preprocessing.signal_check import SignalCheck
from models.data.processing.preprocessing.smooth import Smooth
from models.data.processing.preprocessing.type import PreProcessingType


class PreProcessing:
    pipeline: List[ProcessingNode] = None

    def __init__(self, pipeline: List[ProcessingNode] = None) -> None:
        super().__init__()
        self.pipeline = pipeline

    @classmethod
    def from_config_json(cls):
        pipeline = []
        for preprocessing_node_settings in Configuration.get_preprocessing_settings():
            pipeline.append(PreProcessing._select_processor(preprocessing_node_settings))
        return cls(pipeline=pipeline)

    @staticmethod
    def _select_processor(node_settings: dict) -> ProcessingNode:
        preprocess_type = PreProcessingType[node_settings['type']]
        parameters = node_settings['parameters']

        parameters['sampling-frequency'] = Configuration.get_sampling_frequency()

        processor = None
        if preprocess_type == PreProcessingType.CUSTOM:
            processor = Custom.from_config_json(parameters)

        elif preprocess_type == PreProcessingType.DETREND:
            processor = Detrend.from_config_json(parameters)

        elif preprocess_type == PreProcessingType.FILTER:
            processor = PreProcessing._select_filter(parameters)

        elif preprocess_type == PreProcessingType.DOWNSAMPLE:
            processor = Downsample.from_config_json(parameters)

        elif preprocess_type == PreProcessingType.DENOISE:
            processor = Denoise.from_config_json(parameters)

        elif preprocess_type == PreProcessingType.TRANSFORM:
            raise NotImplementedError("TRANSFORM is not implemented yet")

        elif preprocess_type == PreProcessingType.SMOOTH:
            processor = Smooth.from_config_json(parameters)

        elif preprocess_type == PreProcessingType.SIGNAL_CHECK:
            processor = SignalCheck.from_config_json(parameters)

        else:
            raise ValueError("Invalid preprocessing type " + node_settings['type'])

        return processor

    @staticmethod
    def _select_filter(parameters: dict) -> Filter:
        filter_type = parameters['type']
        if filter_type in ['BANDPASS', 'BANDSTOP']:
            return BandFilter.from_config_json(parameters)
        elif filter_type in ['LOWPASS', 'HIGHPASS']:
            return CutOffFilter.from_config_json(parameters)
        else:
            raise ValueError("Invalid filter type " + filter_type)

    @staticmethod
    def _select_feature_extractor(parameters: dict) -> Filter:
        extractor_type = parameters['type']
        if extractor_type == 'CSP':
            return BandFilter.from_config_json(parameters)
        else:
            raise ValueError("Invalid feature extractor type " + filter_type)

    def process(self, data):
        for node in self.pipeline:
            node.process(data)
