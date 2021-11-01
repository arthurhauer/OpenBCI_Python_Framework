from typing import List

from config.configuration import Configuration
from models.preprocessing.custom import Custom
from models.preprocessing.detrend import Detrend
from models.preprocessing.downsample import Downsample
from models.preprocessing.filter.band_filter import BandFilter
from models.preprocessing.filter.cutoff_filter import CutOffFilter
from models.preprocessing.filter.filter import Filter
from models.preprocessing.node import PreProcessingNode
from models.preprocessing.type import PreProcessingType


class PreProcessing:
    __pipeline: List[PreProcessingNode] = None

    def __init__(self) -> None:
        super().__init__()

    @property
    def _pipeline(self):
        if self.__pipeline is None:
            self.__pipeline = []
            for preprocessing_node_settings in Configuration.get_preprocessing_settings():
                self.__pipeline.append(PreProcessing._select_processor(preprocessing_node_settings))
        return self.__pipeline

    @staticmethod
    def _select_processor(node_settings: dict) -> PreProcessingNode:
        preprocess_type = PreProcessingType[node_settings['type']]
        parameters = node_settings['parameters']
        processor = None
        if preprocess_type == PreProcessingType.CUSTOM:
            processor = Custom(parameters)
        elif preprocess_type == PreProcessingType.DETREND:
            processor = Detrend(parameters)
        elif preprocess_type == PreProcessingType.FILTER:
            processor = PreProcessing._select_filter(parameters)
        elif preprocess_type == PreProcessingType.DOWNSAMPLE:
            processor = Downsample(parameters)
        elif preprocess_type == PreProcessingType.DENOISE:
            raise NotImplementedError("DENOISE is not implemented yet")
        elif preprocess_type == PreProcessingType.TRANSFORM:
            raise NotImplementedError("TRANSFORM is not implemented yet")
        elif preprocess_type == PreProcessingType.SMOOTH:
            raise NotImplementedError("SMOOTH is not implemented yet")
        else:
            raise ValueError("Invalid preprocessing type " + node_settings['type'])
        return processor

    @staticmethod
    def _select_filter(parameters: dict) -> Filter:
        filter_type = parameters['type']
        if filter_type in ['BANDPASS', 'BANDSTOP']:
            return BandFilter(parameters)
        elif filter_type in ['LOWPASS', 'HIGHPASS']:
            return CutOffFilter(parameters)
        else:
            raise ValueError("Invalid filter type " + filter_type)

    def process(self, data):
        for node in self._pipeline:
            node.process(data)
