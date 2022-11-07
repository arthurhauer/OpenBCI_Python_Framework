from __future__ import annotations
import abc
from typing import List


class Node:
    """Abstract base class for processing pipeline execution on this framework.
    """

    def __init__(self, parameters=None) -> None:
        super().__init__()
        if 'module' not in parameters:
            raise ValueError("error"
                             ".missing"
                             ".node"
                             ".module")
        if 'models.node.' not in parameters['module']:
            ValueError('error'
                       '.invalid'
                       '.value'
                       '.node'
                       '.module')
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

        if 'outputs' not in parameters:
            raise ValueError('error'
                             '.missing'
                             '.node'
                             '.outputs')

        self._initialize_buffer_options(parameters['buffer_options'])
        self._type = parameters['type']

        self._clear_input_buffer()
        self._clear_output_buffer()

        self._initialize_children()

    def _clear_input_buffer(self):
        """Sets input buffer to new list for each input name
        """
        self._input_buffer = {}
        for input_name in self._get_inputs():
            self._input_buffer[input_name] = []

    def _clear_output_buffer(self):
        """Sets output buffer to new list for each output name
        """
        self._output_buffer = {}
        for output_name in self._get_outputs():
            self._output_buffer[output_name] = []

    def _insert_new_input_data(self, data: list, input_name: str):
        """Appends new data to the end of already existing input buffer

        :param data: Data to be added. Should be in channel X sample format
        :type data: list
        :param input_name: Node input name.
        :type input_name: str
        """
        if data is None or len(data) == 0:
            return

        if hasattr(data[0], '__len__') and (not isinstance(data[0], str)):
            for channel_index, channel_data in enumerate(data):
                try:
                    self._input_buffer[input_name][channel_index]
                except IndexError:
                    self._input_buffer[input_name].append([])
                self._input_buffer[input_name][channel_index].extend(channel_data)
        else:
            self._input_buffer[input_name].extend(data)

    def _insert_new_output_data(self, data: list, output_name: str):
        """Appends new data to the end of already existing output buffer

        :param data: Data to be added. Should be in channel X sample format
        :type data: list
        :param output_name: Node output name.
        :type output_name: str
        """
        if data is None or len(data) == 0:
            return

        if hasattr(data[0], '__len__') and (not isinstance(data[0], str)):
            for channel_index, channel_data in enumerate(data):
                try:
                    self._output_buffer[output_name][channel_index]
                except IndexError:
                    self._output_buffer[output_name].append([])
                self._output_buffer[output_name][channel_index].extend(channel_data)
        else:
            self._output_buffer[output_name].extend(data)

    def _initialize_children(self):
        """Sets child nodes dictionary to a new, empty dict
        """
        self._children = {}
        for output_name in self._get_outputs():
            self._children[output_name] = []

    def add_child(self, output_name: str, node: Node, input_name: str):
        """Adds a new child node to child nodes dictionary

        :param output_name: Current node output name, used as key.
        :type output_name: str
        :param node: Child node object.
        :type node: Node
        :param input_name: Child node input name.
        :type input_name: str
        """
        self._children[output_name].append(lambda data: node.run(data, input_name))

    def _call_children(self):
        """Calls child nodes to execute their processing given current node output buffer content.
        """
        for output_name in self._get_outputs():
            output = self._output_buffer[output_name]
            output_children = self._children[output_name]
            for child in output_children:
                child(output)

    def run(self, data: list = None, input_name: str = None) -> None:
        """Run node main function

        :param data: Node input data (channel X sample). Can be None if node takes no input data.
        :type data: list
        :param input_name: Node input name. Can be None if node takes no input data.
        :type input_name: str
        """
        self._run(data, input_name)
        if not self._is_next_node_call_enabled():
            return
        self._call_children()

    def check_input(self, input_name: str) -> None:
        if input_name not in self._get_inputs():
            raise ValueError('error'
                             '.invalid'
                             '.value'
                             '.node'
                             '.input')

    def check_output(self, output_name: str) -> None:
        if output_name not in self._get_outputs():
            raise ValueError('error'
                             '.invalid'
                             '.value'
                             '.node'
                             '.output')

    @classmethod
    @abc.abstractmethod
    def from_config_json(cls, parameters: dict):
        """Returns node instance from given parameters in dict form

        :param parameters: Node parameters in dict form.
        :type parameters: dict
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def _run(self, data: list, input_name: str) -> None:
        """Node self implementation of processing on input data

        :param data: Node input data.
        :type data: list
        :param input_name: Node input name.
        :type input_name: str
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def _is_next_node_call_enabled(self) -> bool:
        """Node self implementation to check if child nodes should be called.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def _initialize_buffer_options(self, buffer_options: dict) -> None:
        """Node self implementation of buffer behaviour options initialization

        :param buffer_options: Buffer behaviour options.
        :type buffer_options: dict
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def _get_inputs(self) -> List[str]:
        """Returns the input names in list form.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def _get_outputs(self) -> List[str]:
        """Returns the output names in list form.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def dispose(self) -> None:
        """Node self implementation of disposal of allocated resources.
        """
        raise NotImplementedError()
