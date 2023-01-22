import abc
from abc import ABC

from models.framework_data import FrameworkData
from models.node.generator.generator_node import GeneratorNode


class SingleRunGeneratorNode(GeneratorNode):

    def __init__(self, parameters=None):
        super().__init__(parameters)

    def _disable_next_node_call(self) -> bool:
        return False

    def run(self, data: FrameworkData = None, input_name: str = None) -> None:
        super().run()
        # noinspection PyAttributeOutsideInit
        self._is_next_node_call_enabled = self._disable_next_node_call
