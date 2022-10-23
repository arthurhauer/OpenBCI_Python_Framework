from __future__ import annotations
import abc


class Node:

    def __init__(self, parameters=None) -> None:
        super().__init__()
        if 'module' not in parameters:
            raise ValueError("error"
                             ".missing"
                             ".node"
                             ".module")
        if 'type' not in parameters:
            raise ValueError("error"
                             ".missing"
                             ".node"
                             ".type")

        if 'buffer_options' not in parameters:
            raise ValueError('error'
                             '.missing'
                             '.node'
                             '.buffer_options')

        if 'children' not in parameters:
            raise ValueError('error'
                             '.missing'
                             '.node'
                             '.children')

        self._initialize_buffer_options(parameters['buffer_options'])
        self._type = parameters['type']

        self._clear_input_buffer()
        self._clear_output_buffer()

        self._initialize_children()

    def _clear_input_buffer(self):
        self._input_buffer = []

    def _clear_output_buffer(self):
        self._output_buffer = []

    def _insert_new_input_data(self, data: list):
        self._input_buffer.extend(data)

    def _insert_new_output_data(self, data: list):
        self._output_buffer.extend(data)

    def _initialize_children(self):
        self._children = {}

    def add_child(self, name: str, node: Node):
        self._children[name] = node

    def _call_children(self):
        for key in self._children:
            self._children[key].run(list)

    def run(self, data: list = None) -> None:
        self._run(data)
        if not self._is_next_node_call_enabled():
            return
        self._call_children()

    @classmethod
    @abc.abstractmethod
    def from_config_json(cls, parameters: dict):
        raise NotImplementedError()

    @abc.abstractmethod
    def _run(self, data: list) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def _is_next_node_call_enabled(self) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def _initialize_buffer_options(self, buffer_options: dict) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def dispose(self) -> None:
        raise NotImplementedError()