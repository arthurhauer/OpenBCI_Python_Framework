from abc import ABC

from models.framework_data import FrameworkData
from models.node.generator.generator_node import GeneratorNode


class SingleRunGeneratorNode(GeneratorNode):

    def __init__(self, parameters=None):
        self._first_execution = True
        super().__init__(parameters)

    def run(self, data: FrameworkData = None, input_name: str = None) -> None:
        if self._first_execution:
            super().run()
            self._first_execution = False
        else:
            raise Exception("Stop Executing!")
