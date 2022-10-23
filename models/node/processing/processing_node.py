import abc

from models.node.node import Node


class ProcessingNode(Node):

    def __init__(self, parameters=None) -> None:
        super().__init__(parameters=parameters)

    def _initialize_buffer_options(self, buffer_options: dict) -> None:
        if 'clear_output_buffer_on_data_input' not in buffer_options:
            raise ValueError('error'
                             '.missing'
                             '.node'
                             '.buffer_options'
                             '.processing'
                             '.clear_output_buffer_on_data_input')
        if 'clear_input_buffer_after_process' not in buffer_options:
            raise ValueError('error'
                             '.missing'
                             '.node'
                             '.buffer_options'
                             '.processing'
                             '.clear_input_buffer_after_process')
        if 'clear_output_buffer_after_process' not in buffer_options:
            raise ValueError('error'
                             '.missing'
                             '.node'
                             '.buffer_options'
                             '.processing'
                             '.clear_output_buffer_after_process')
        self._clear_output_buffer_on_data_input = buffer_options['clear_output_buffer_on_data_input']
        self._clear_input_buffer_after_process = buffer_options['clear_input_buffer_after_process']
        self._clear_output_buffer_after_process = buffer_options['clear_output_buffer_after_process']

    def _run(self, data: list) -> None:
        self._input_buffer.extend(data)
        if self._clear_output_buffer_on_data_input:
            self._clear_output_buffer()
        self._process_input_buffer()

    def _process_input_buffer(self):
        if not self._is_processing_condition_satisfied():
            return
        processed_data = self._process(self._input_buffer)
        if self._clear_input_buffer_after_process:
            self._clear_input_buffer()
        if self._clear_output_buffer_after_process:
            self._clear_output_buffer()
        self._output_buffer.extend(processed_data)

    @classmethod
    @abc.abstractmethod
    def from_config_json(cls, parameters: dict):
        raise NotImplementedError()

    @abc.abstractmethod
    def _is_next_node_call_enabled(self) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def _is_processing_condition_satisfied(self) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def _process(self, data: list) -> list:
        raise NotImplementedError()

    def dispose(self) -> None:
        return
