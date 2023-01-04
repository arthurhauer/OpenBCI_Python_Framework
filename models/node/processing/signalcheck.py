import abc
from typing import List, Final, Dict

from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode
from typing import List


class SignalCheck(ProcessingNode):
    _MODULE_NAME: Final[str] = 'node.processing.signalcheck'

    INPUT_MAIN: Final[str] = 'main'
    OUTPUT_MAIN: Final[str] = 'main'

    @abc.abstractmethod
    def _initialize_parameter_fields(self, parameters: dict):
        super()._initialize_parameter_fields(parameters)

    def _is_next_node_call_enabled(self) -> bool:
        return True

    def _is_processing_condition_satisfied(self) -> bool:
        # TODO change
        return True

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        # TODO change
        print('SignalCheck!')
        return data

    def _get_inputs(self) -> List[str]:
        return [
            self.INPUT_MAIN
        ]

    def _get_outputs(self) -> List[str]:
        return [
            self.OUTPUT_MAIN
        ]
