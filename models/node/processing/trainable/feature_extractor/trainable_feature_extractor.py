import abc
from typing import List, Dict, Final
from models.framework_data import FrameworkData
from models.node.processing.trainable.trainable_processing_node import TrainableProcessingNode


class TrainableFeatureExtractor(TrainableProcessingNode):
    _MODULE_NAME: Final[str] = 'node.processing.trainable.feature_extractor.feature_extractor'

    OUTPUT_MAIN: Final[str] = 'main'

    def __init__(self, parameters: dict):
        super().__init__(parameters)
        self._validate_parameters(parameters)

    @abc.abstractmethod
    def _validate_parameters(self, parameters: dict):
        super()._validate_parameters(parameters)

    @classmethod
    def from_config_json(cls, parameters: dict):
        return cls(parameters)

    def _is_next_node_call_enabled(self) -> bool:
        return True

    def _is_processing_condition_satisfied(self) -> bool:
        return self._input_buffer[self.INPUT_DATA].get_data_count() > 0

    @abc.abstractmethod
    def _is_training_condition_satisfied(self) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def _should_retrain(self) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        extracted_data: Dict[str, FrameworkData] = {}
        for key in data:
            extracted_data[key] = FrameworkData(sampling_frequency_hz=data[key].sampling_frequency)
            raw_data: FrameworkData = data[key]
            self._extract_data(raw_data)
        return extracted_data

    @abc.abstractmethod
    def _train(self, data: FrameworkData, label: FrameworkData):
        raise NotImplementedError()

    @abc.abstractmethod
    def _extract_data(self, data: FrameworkData) -> FrameworkData:
        raise NotImplementedError()

    @abc.abstractmethod
    def _get_outputs(self) -> List[str]:
        return [
            self.OUTPUT_MAIN
        ]
