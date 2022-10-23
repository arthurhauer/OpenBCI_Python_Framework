import abc

from models.node.node import Node


class GeneratorNode(Node):

    def __init__(self, parameters=None) -> None:
        super().__init__(parameters=parameters)

    def _initialize_buffer_options(self, buffer_options: dict) -> None:
        if 'clear_output_buffer_on_generate' not in buffer_options:
            raise ValueError('error'
                             '.missing'
                             '.node'
                             '.buffer_options'
                             '.generator'
                             '.clear_output_buffer_on_generate')
        self._clear_output_buffer_on_generate = buffer_options['clear_output_buffer_on_generate']

    def _run(self, data: list) -> None:
        if self._clear_output_buffer_on_generate:
            super()._clear_output_buffer()

        data = self._generate_data()
        self._insert_new_output_data(data)

    @classmethod
    @abc.abstractmethod
    def from_config_json(cls, parameters: dict):
        raise NotImplementedError()

    @abc.abstractmethod
    def _is_next_node_call_enabled(self) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def _is_generate_data_condition_satisfied(self) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def _generate_data(self) -> list:
        raise NotImplementedError()
