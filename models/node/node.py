from __future__ import annotations
import abc
import copy
import threading
import traceback
import time
from queue import Queue
from threading import Thread
from typing import List, Dict, Final, Any

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData


# TODO Isolamento de nodes em threads separadas. Cada nó deve ser executado em uma thread
class Node:
    _MODULE_NAME: Final[str] = 'models.node'
    """Abstract base class for processing pipeline execution on this framework.
        A node is a component that receives data from its inputs, process it and send it to its outputs.
    """

    def __init__(self, parameters=None) -> None:
        super().__init__()
        self.name: Final[str] = parameters['name']
        self._enable_log = True
        self.print("Initializing")
        self._validate_parameters(parameters)
        self.parameters = parameters

        self._initialize_buffer_options(parameters['buffer_options'])
        self._type: Final[str] = parameters['type']

        self._initialize_parameter_fields(parameters)

        self._clear_input_buffer()
        self._clear_output_buffer()

        self._initialize_children()

        self._child_input_relation: Dict[Node, List[str]] = {}

        # Threading attributes
        self.local_storage = Queue()
        self.running = False
        self.thread = None
        self.new_data_available = False
        self.condition = threading.Condition()

    def _build_graph_inputs(self):
        return f"""
                <TR>
                  <TD BORDER="0">
                     <TABLE BORDER="0" CELLBORDER="" CELLSPACING="0" CELLPADDING="0">
                        <TR>
                           <TD WIDTH="20"></TD>
                           {[f'<TD PORT="in_{input_name}" BORDER="1" CELLPADDING="1"><FONT POINT-SIZE="8">{input_name}</FONT></TD><TD WIDTH="10"></TD>' for input_name in self._get_inputs()]}
                           <TD WIDTH="10"></TD>
                        </TR>
                     </TABLE>
                  </TD>
               </TR>
        """

    def _build_graph_outputs(self):
        return f"""
                <TR>
                  <TD BORDER="0">
                     <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="0">
                        <TR>
                           <TD WIDTH="20"></TD>
                           {[f'<TD PORT="out_{output_name}" BORDER="1" CELLPADDING="1"><FONT POINT-SIZE="8">{output_name}</FONT></TD><TD WIDTH="10"></TD>' for output_name in self._get_outputs()]}
                           <TD WIDTH="10"></TD>
                        </TR>
                     </TABLE>
                  </TD>
               </TR>
        """

    def build_graphviz_representation(self):
        return f"""
        {self.name} [
      shape=plaintext
      tooltip="{self.parameters}"
      label=<
            <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="0">
               {self._build_graph_inputs()}
               <TR>
                  <TD BORDER="1" STYLE="ROUNDED" CELLPADDING="4" COLOR="black">{self.name}<BR/><FONT POINT-SIZE="5">{self._MODULE_NAME}</FONT></TD>
               </TR>
               {self._build_graph_outputs()}
            </TABLE>
        >
      ];
        """

    @abc.abstractmethod
    def _validate_parameters(self, parameters: dict):
        """
        Validates parameters passed to this node.

        :param parameters: Parameters passed to this node.
        :type parameters: dict
        :raises MissingParameterError: If a required parameter is missing.
        """
        if 'module' not in parameters:
            raise MissingParameterError(
                module=self._MODULE_NAME, name=self.name,
                parameter='module'
            )
        if 'models.node.' not in parameters['module']:
            raise InvalidParameterValue(
                module=self._MODULE_NAME, name=self.name,
                parameter='module',
                cause='must_be_part_of_[models.node]_module'
            )
        if 'type' not in parameters:
            raise MissingParameterError(
                module=self._MODULE_NAME, name=self.name,
                parameter='type'
            )
        if 'enable_log' not in parameters:
            parameters['enable_log'] = False
        if 'buffer_options' not in parameters:
            raise MissingParameterError(
                module=self._MODULE_NAME, name=self.name,
                parameter='buffer_options'
            )
        if 'outputs' not in parameters:
            raise MissingParameterError(
                module=self._MODULE_NAME, name=self.name,
                parameter='outputs'
            )
        if 'name' not in parameters:
            raise MissingParameterError(
                module=self._MODULE_NAME, name=self.name,
                parameter='name'
            )

        if 'print_buffer_size' not in parameters['buffer_options']:
            parameters['buffer_options']['print_buffer_size'] = False
        elif type(parameters['buffer_options']['print_buffer_size']) is not bool:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='buffer_options.print_buffer_size',
                                        cause='must_be_bool')

    @abc.abstractmethod
    def _initialize_parameter_fields(self, parameters: dict):
        """
        Initializes parameter fields of this node. This is an abstract method and should be implemented by subclasses.

        :param parameters: Parameters passed to this node.
        :type parameters: dict
        """
        self._enable_log = parameters['enable_log']
        self._should_print_buffer_size = parameters['buffer_options']['print_buffer_size']
        return

    def _clear_input_buffer(self):
        """Sets input buffer to new empty object for each input name
        """
        self._input_buffer = {}
        for input_name in self._get_inputs():
            self._input_buffer[input_name] = FrameworkData()

    def _clear_output_buffer(self):
        """Sets output buffer to new empty object for each output name
        """
        self._output_buffer = {}
        for output_name in self._get_outputs():
            self._output_buffer[output_name] = FrameworkData()

    @staticmethod
    def _insert_data_in_buffer(data: FrameworkData, buffer_data_name: str, buffer: Dict[str, FrameworkData]):
        buffer[buffer_data_name].extend(copy.deepcopy(data))

    def _print_buffer_size(self, buffer_name: str, buffer: Dict[str, FrameworkData]):
        formatted_buffer_sizes = f'Buffer:{buffer_name}\t'
        for key in buffer:
            formatted_buffer_sizes += f'###Key:{key}=Length:{buffer[key].get_data_count()}### '
        self.print(formatted_buffer_sizes)

    def _insert_new_input_data(self, data: FrameworkData, input_name: str):
        """Appends new data to the end of already existing input buffer

        :param data: Data to be added. Should be in channel X sample format
        :type data: FrameworkData
        :param input_name: Node input name.
        :type input_name: str
        """
        self._input_buffer[input_name].extend(copy.deepcopy(data))
        if self._should_print_buffer_size:
            self._print_buffer_size('input', self._input_buffer)

    def _insert_new_output_data(self, data: FrameworkData, output_name: str):
        """
        Appends new data to the end of already existing output buffer

        :param data: Data to be added. Should be in channel X sample format
        :type data: FrameworkData
        :param output_name: Node output name.
        :type output_name: str
        """
        self._output_buffer[output_name].extend(copy.deepcopy(data))
        if self._should_print_buffer_size:
            self._print_buffer_size('output', self._output_buffer)

    def _initialize_children(self):
        """Sets child nodes dictionary to a new, empty dict
        """
        self._children: Dict[str, List[Dict[str, Any]]] = {}
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
        # TODO Melhorar o objeto guardado em self._children
        if node not in self._child_input_relation:
            self._child_input_relation[node] = []
        if input_name in self._child_input_relation[node]:
            raise InvalidParameterValue(module='node', parameter=f'outputs.{output_name}', cause='already_added',
                                        name=self.name)
        self._children[output_name].append(
            {
                'node': node,
                'run': lambda data: node.run(data, input_name),
                'run_': lambda data: node.run(),
                'dispose': lambda x: node.dispose()
            }
        )

    def _dispose_all_children(self):
        for output_name in self._get_outputs():
            output_children = self._children[output_name]
            for child in output_children:
                child['dispose'](child)

    def _call_children(self):
        """Calls child nodes to execute their processing given current node output buffer content.
        """
        for output_name in self._get_outputs():
            output = self._output_buffer[output_name]
            output_children = self._children[output_name]
            for child in output_children:
                child['run'](output)

    def _thread_runner(self):
        while self.running:
            with self.condition:
                while not self.new_data_available and self.running:
                    self.condition.wait()
                if not self.running:
                    break
                while not self.local_storage.empty():
                    input_name, data = self.local_storage.get()
                    try:
                        self._run(data, input_name)
                    except Exception as e:
                        self.print(f'Error: {e}', exception=e)
                        raise e
                    if self._is_next_node_call_enabled():
                        self._call_children()
                self.new_data_available = False

    def run(self, data: FrameworkData = None, input_name: str = None) -> None:
        self.local_storage.put((input_name, data))
        with self.condition:
            self.new_data_available = True
            self.condition.notify()

        if not self.running:
            self.running = True
            self.thread = Thread(target=self._thread_runner, name=self.name)
            self.thread.start()

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
    def from_config_json(cls, parameters: dict):
        """Returns node instance from given parameters in dict form

        :param parameters: Node parameters in dict form.
        :type parameters: dict
        """
        return cls(parameters)

    @abc.abstractmethod
    def _run(self, data: FrameworkData, input_name: str) -> None:
        """Node self implementation of processing on input data

        :param data: Node input data.
        :type data: FrameworkData
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

    def dispose_all(self) -> None:
        """Disposes itself and all its children nodes
        """
        self._dispose_all_children()
        self.dispose()

    @abc.abstractmethod
    def dispose(self) -> None:
        """Node self implementation of disposal of allocated resources.
        """
        self.print('Disposing...')
        self.running = False
        with self.condition:
            self.condition.notify()
        if self.thread:
            self.thread.join()
        return

    def print(self, message: str, exception: Exception = None) -> None:
        if self._enable_log or not exception is None:
            print(f'{time.time()} - {self._MODULE_NAME}.{self.name} - {message}')
            if exception:
                print('Stack trace:')
                traceback.print_exc()

    @property
    def module_name(self):
        return self._MODULE_NAME
