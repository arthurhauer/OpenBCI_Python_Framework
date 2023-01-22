import abc
from typing import List

from models.framework_data import FrameworkData
from models.node.node import Node


class OutputNode(Node):

    def __init__(self, parameters: dict):
        super().__init__(parameters=parameters)

    @abc.abstractmethod
    def _validate_parameters(self, parameters: dict):
        super()._validate_parameters(parameters)

    @abc.abstractmethod
    def _run(self, data: FrameworkData, input_name: str) -> None:
        raise NotImplementedError()

    def _is_next_node_call_enabled(self) -> bool:
        return False

    def _initialize_buffer_options(self, buffer_options: dict) -> None:
        pass

    @abc.abstractmethod
    def _get_inputs(self) -> List[str]:
        raise NotImplementedError()

    def _get_outputs(self) -> List[str]:
        return []

    def dispose(self) -> None:
        super().dispose()
