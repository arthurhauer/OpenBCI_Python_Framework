from models.preprocessing.custom import Custom
from models.preprocessing.detrend import Detrend
from models.preprocessing.filter.band_filter import BandFilter
from models.preprocessing.filter.cutoff_filter import CutOffFilter
from models.preprocessing.filter.filter import Filter
from models.preprocessing.processor import Processor
from models.preprocessing.type import PreProcessingType


class PreProcessingNode:
    _parameters: dict = {}
    _processor: Processor

    def __init__(self, config: dict) -> None:
        super().__init__()
        preprocess_type = PreProcessingType[config['type']]
        parameters = config['parameters']
        if preprocess_type == PreProcessingType.FILTER:
            self._processor = self._select_filter(parameters)
        elif preprocess_type == PreProcessingType.DETREND:
            self._processor = Detrend(parameters)
        elif preprocess_type == PreProcessingType.CUSTOM:
            self._processor = Custom(parameters)
        else:
            raise ValueError("Invalid preprocessing type " + config['type'])

    def _select_filter(self, parameters: dict) -> Filter:
        filter_type = parameters['type']
        if filter_type in ['BANDPASS', 'BANDSTOP']:
            return BandFilter(parameters)
        elif filter_type in ['LOWPASS', 'HIGHPASS']:
            return CutOffFilter(parameters)
        else:
            raise ValueError("Invalid filter type " + filter_type)

    def process(self,data):
        return self._processor.process(data)
