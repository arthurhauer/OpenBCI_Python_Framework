from __future__ import annotations
import abc


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
        """Sets input buffer to new list
        """
        self._input_buffer = []

    def _clear_output_buffer(self):
        """Sets output buffer to new list
        """
        self._output_buffer = []

    def _insert_new_input_data(self, data: list):
        """Appends new data to the end of already existing input buffer

        :param data: Data to be added. Should be in sample X channel format
        :type data: list
        """
        self._input_buffer.extend(data)

    def _insert_new_output_data(self, data: list):
        """Appends new data to the end of already existing output buffer

        :param data: Data to be added. Should be in sample X channel format
        :type data: list
        """
        self._output_buffer.extend(data)

    def _initialize_children(self):
        """Sets child nodes dictionary to a new, empty dict
        """
        self._children = {}

    def add_child(self, name: str, node: Node):
        """Adds a new child node to child nodes dictionary

        :param name: Child node name, used as key.
        :type name: str
        :param node: Child node object.
        :type node: Node
        """
        self._children[name] = node

    def _call_children(self):
        """Calls child nodes to execute their processing given current node output buffer content.
        """
        for key in self._children:
            self._children[key].run(self._output_buffer)

    def run(self, data: list = None) -> None:
        """Run node main function

        :param data: Node input data (sample X channel). Can be None if node takes no input data.
        :type data: list
        """
        self._run(data)
        if not self._is_next_node_call_enabled():
            return
        self._call_children()

    @classmethod
    @abc.abstractmethod
    def from_config_json(cls, parameters: dict):
        """Returns node instance from given parameters in dict form

        :param parameters: Node parameters in dict form.
        :type parameters: dict
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def _run(self, data: list) -> None:
        """Node self implementation of processing on input data

        :param data: Node input data.
        :type data: list
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
    def dispose(self) -> None:
        """Node self implementation of disposal of allocated resources.
        """
        raise NotImplementedError()