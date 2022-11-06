from typing import Dict

import time
import importlib

from config.configuration import Configuration
from models.node.generator.generator_node import GeneratorNode
from models.node.node import Node


class Application:

    def __init__(self) -> None:
        super().__init__()
        self._initialize_nodes()
        for key in Configuration.get_root_nodes():
            node_config = Configuration.get_root_nodes()[key]
            node = self.get_generator_node_from_module_and_type(
                node_config['module'],
                node_config['type']
            )
            root_node: GeneratorNode = node.from_config_json(node_config)
            for output_name in node_config['outputs']:
                root_node.check_output(output_name)
                for output_config in node_config['outputs'][output_name]:
                    child_node = self._get_node(output_config['node'])
                    child_node.check_input(output_config['input'])
                    root_node.add_child(output_name, child_node, output_config['input'])
            self._add_root_node(
                key,
                root_node)
        while True:
            self.run()
            time.sleep(1)

    @staticmethod
    def get_generator_node_from_module_and_type(module: str, node_type: str) -> GeneratorNode:
        module = importlib.import_module(module + '.' + node_type.lower())
        class_: GeneratorNode = getattr(module, node_type)
        return class_

    @staticmethod
    def get_node_from_module_and_type(module: str, node_type: str) -> Node:
        module = importlib.import_module(module + '.' + node_type.lower())
        class_: GeneratorNode = getattr(module, node_type)
        return class_

    def _get_node(self, node_name: str) -> Node:
        if node_name not in self._nodes:
            node_config = Configuration.get_common_nodes()[node_name]
            node_type = self.get_node_from_module_and_type(
                node_config['module'],
                node_config['type']
            )
            node: Node = node_type.from_config_json(node_config)
            for output_name in node_config['outputs']:
                for output_config in node_config['outputs'][output_name]:
                    child_node = self._get_node(output_config['node'])
                    child_node.check_input(output_config['input'])
                    node.add_child(output_name, child_node, output_config['input'])
            self._nodes[node_name] = node
        return self._nodes[node_name]

    def _initialize_nodes(self):
        self._nodes: Dict[str, Node] = {}
        self._root_nodes: Dict[str, GeneratorNode] = {}

    def _add_root_node(self, name: str, node: GeneratorNode):
        self._root_nodes[name] = node

    def run(self):
        for key in self._root_nodes:
            self._root_nodes[key].run()
