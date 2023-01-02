import abc
from typing import List, Dict, Final
from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode


class FeatureExtractor(ProcessingNode):
    _MODULE_NAME: Final[str] = 'node.processing.feature_extractor.feature_extractor'

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
        return self._input_buffer[self.INPUT_MAIN].get_data_count() > 0

    @abc.abstractmethod
    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        raise NotImplementedError()

    @abc.abstractmethod
    def _get_inputs(self) -> List[str]:
        raise NotImplementedError()

    @abc.abstractmethod
    def _get_outputs(self) -> List[str]:
        raise NotImplementedError()
