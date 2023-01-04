import abc
from typing import List, Dict, Final
from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode


class Segmenter(ProcessingNode):
    _MODULE_NAME: Final[str] = 'node.processing.segmenter.segmenter'

    INPUT_MAIN: Final[str] = 'main'
    OUTPUT_MAIN: Final[str] = 'main'

    def __init__(self, parameters: dict):
        super().__init__(parameters)
        self._validate_parameters(parameters)

    @abc.abstractmethod
    def _validate_parameters(self, parameters: dict):
        raise NotImplementedError()

    @classmethod
    def from_config_json(cls, parameters: dict):
        return cls(parameters)

    def _is_next_node_call_enabled(self) -> bool:
        return True

    def _is_processing_condition_satisfied(self) -> bool:
        return self._input_buffer[self.INPUT_MAIN].get_data_count() > 0

    @abc.abstractmethod
    def segment_data(self, data: FrameworkData) -> FrameworkData:
        raise NotImplementedError()

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        segmented_data: Dict[str, FrameworkData] = {}
        for key in data:
            segmented_data[key] = self.segment_data(data[key])
        return segmented_data

    def _get_inputs(self) -> List[str]:
        return [
            self.INPUT_MAIN
        ]

    def _get_outputs(self) -> List[str]:
        return [
            self.OUTPUT_MAIN
        ]
