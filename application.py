import os
from typing import Dict
from threading import Thread, Event
import time
import importlib
from config.configuration import Configuration
from models.exception.invalid_parameter_value import InvalidParameterValue
from models.node.generator.generator_node import GeneratorNode
from models.node.node import Node
from graphviz import Source


class Application:

    def __init__(self, configuration: dict) -> None:
        print('Starting application')
        print('Loading configuration')
        self.configuration = Configuration(configuration)
        super().__init__()
        self._stop_execution = False
        self.graphviz_representation = 'digraph G {'
        self._initialize_nodes()
        self.graphviz_representation += '\n}'
        os.environ["PATH"] += os.pathsep + f'.{os.sep}lib{os.sep}Graphviz'
        if self.configuration.show_diagram():
            src = Source(self.graphviz_representation, format='svg')
            src.render(filename='graph', directory=f'output{os.sep}')
            src.view()
        print('Starting pipeline execution')
        self._terminate_event = Event()
        self._execution_thread = Thread(target=self._run_loop)
        self._execution_thread.start()

    def _run_loop(self):
        while not self._terminate_event.is_set():
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
            node_config = self.configuration.get_common_nodes()[node_name]
            node_type = self.get_node_from_module_and_type(
                node_config['module'],
                node_config['type']
            )
            node_config['name'] = node_name
            node: Node = node_type.from_config_json(node_config)
            self.graphviz_representation += f'\n{node.build_graphviz_representation()}'
            for output_name in node_config['outputs']:
                if type(node_config['outputs'][output_name]) is not list:
                    raise InvalidParameterValue(module=node.module_name,
                                                name=node.name,
                                                parameter=f'outputs.{output_name}',
                                                cause='must_be_list')
                edge_color: str = 'red' if len(node_config['outputs'][output_name]) > 1 else 'blue'

                for output_config in node_config['outputs'][output_name]:
                    child_node_key = output_config['node']
                    child_node = self._get_node(child_node_key)
                    input = output_config['input']
                    self.graphviz_representation += f'\n{node_name}:out_{output_name} -> {child_node_key}:in_{input} [color={edge_color}]'
                    try:
                        child_node.check_input(output_config['input'])
                    except Exception as e:
                        print(
                            f'error in {node_name} output {output_name} config: {child_node.name} doesnt have configured input {input}')
                        raise e
                    node.add_child(output_name, child_node, input)
            self._nodes[node_name] = node
        return self._nodes[node_name]

    def _initialize_nodes(self):
        print('Initializing nodes')
        self._nodes: Dict[str, Node] = {}
        self._root_nodes: Dict[str, GeneratorNode] = {}
        for key in self.configuration.get_root_nodes():
            node_config = self.configuration.get_root_nodes()[key]
            node = self.get_generator_node_from_module_and_type(
                node_config['module'],
                node_config['type']
            )
            node_config['name'] = key
            root_node: GeneratorNode = node.from_config_json(node_config)
            self.graphviz_representation += f'\n{root_node.build_graphviz_representation()}'
            for output_name in node_config['outputs']:
                root_node.check_output(output_name)
                edge_color: str = 'red' if len(node_config['outputs'][output_name]) > 1 else 'blue'
                for output_config in node_config['outputs'][output_name]:
                    child_node_key = output_config['node']
                    child_node = self._get_node(child_node_key)
                    input = output_config['input']
                    self.graphviz_representation += f'\n{key}:out_{output_name} -> {child_node_key}:in_{input} [color={edge_color}]'
                    try:
                        child_node.check_input(output_config['input'])
                    except Exception as e:
                        print(
                            f'error in {key} output {output_name} config: {child_node.name} doesnt have configured input {input}')
                        raise e
                    root_node.add_child(output_name, child_node, output_config['input'])
            self._add_root_node(
                key,
                root_node)
        print('Nodes initialized')

    def _add_root_node(self, name: str, node: GeneratorNode):
        self._root_nodes[name] = node

    def run(self):
        for key in self._root_nodes:
            try:
                self._root_nodes[key].run()
            except Exception as e:
                self.dispose()
                raise e

    def dispose(self):
        print('Disposing application')
        self._terminate_event.set()
        self._stop_execution = True
        self._execution_thread.join()
        for key in self._root_nodes:
            self._root_nodes[key].dispose_all()
        print('Application disposed')
