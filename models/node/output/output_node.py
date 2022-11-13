from typing import List

from models.framework_data import FrameworkData
from models.node.node import Node


class OutputNode(Node):
    # TODO implementar
    def __init__(self, parameters: dict):
        super().__init__(parameters=parameters)

        @classmethod
        def from_config_json(cls, parameters: dict):
            return cls(parameters=parameters)

        def _run(self, data: FrameworkData, input_name: str) -> None:
            pass

        def _is_next_node_call_enabled(self) -> bool:
            pass

        def _initialize_buffer_options(self, buffer_options: dict) -> None:
            pass

        def _get_inputs(self) -> List[str]:
            pass

        def _get_outputs(self) -> List[str]:
            pass

        def dispose(self) -> None:
            pass
