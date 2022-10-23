from threading import Thread

import numpy
import time
from nptyping import Float
from numpy.typing import NDArray
import importlib

from config.configuration import Configuration
from models.node.generator.generator_node import GeneratorNode
from models.node.generator.openbciboard import OpenBCIBoard


class Application:

    def __init__(self) -> None:
        super().__init__()
        self._initialize_root_nodes()
        for key in Configuration.get_nodes():
            node_config = Configuration.get_nodes()[key]
            node = self.get_generator_node_from_module_and_type(
                node_config['module'],
                node_config['type']
            )
            self._add_root_node(
                key,
                node.from_config_json(node_config))
        while True :
            self.run()
            time.sleep(1)

    @staticmethod
    def get_generator_node_from_module_and_type(module: str, node_type: str) -> GeneratorNode:
        module = importlib.import_module(module + '.' + node_type.lower())
        class_: GeneratorNode = getattr(module, node_type)
        return class_

    def _initialize_root_nodes(self):
        self._root_nodes: dict = {}

    def _add_root_node(self, name: str, node: GeneratorNode):
        self._root_nodes[name] = node

    def run(self):
        for key in self._root_nodes:
            self._root_nodes[key].run()
