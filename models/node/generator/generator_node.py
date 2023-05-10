import abc
from typing import List, Dict

from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.node import Node


class GeneratorNode(Node):
    """This node is the basic implementation of the nodes that generates data. It contains the basic methods that are
    common to all the generator nodes, so that it can be inherited by the other generator nodes.

    :param parameters: The parameters that were passed to the node. This comes from the configuration file.
    :type parameters: dict

    :raises MissingParameterError: The ``buffer_options`` dictionary is required.
    """

    def __init__(self, parameters=None) -> None:
        super().__init__(parameters=parameters)

    def _validate_parameters(self, parameters: dict):
        """Validates the parameters that were passed to the node. This comes from the configuration file.

        :param parameters: The parameters that were passed to the node. This comes from the configuration file.
        :type parameters: dict

        :raises MissingParameterError: The ``buffer_options`` dictionary is required.

        ``config.json`` example:
            **clear_output_buffer_on_generate** (*bool*): If ``True``, the output buffer will be cleared when the node is executed.

        """
        super()._validate_parameters(parameters)
        if 'clear_output_buffer_on_generate' not in parameters['buffer_options']:
            raise MissingParameterError(module=self._MODULE_NAME,name=self.name,
                                        parameter='buffer_options.clear_output_buffer_on_generate')

    def _initialize_parameter_fields(self, parameters: dict):
        """Initializes the parameter fields of the node.
        """
        super()._initialize_parameter_fields(parameters)

    def _initialize_buffer_options(self, buffer_options: dict) -> None:
        """Initializes the buffer options of the node.
        """
        self._clear_output_buffer_on_generate = buffer_options['clear_output_buffer_on_generate']

    def _run(self, data: FrameworkData, input_name: str) -> None:
        """This method is called when the node is executed. If the generate data condition is satisfied, it generates
        data and inserts it into the output buffer.
        """
        if not self._is_generate_data_condition_satisfied():
            return

        if self._clear_output_buffer_on_generate:
            super()._clear_output_buffer()

        data = self._generate_data()
        for output_name in self._get_outputs():
            self._insert_new_output_data(data[output_name], output_name)

    @abc.abstractmethod
    def _is_next_node_call_enabled(self) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def _is_generate_data_condition_satisfied(self) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def _generate_data(self) -> Dict[str, FrameworkData]:
        raise NotImplementedError()

    def _get_inputs(self) -> List[str]:
        """Returns the input names in list form.
        """
        return []

    @abc.abstractmethod
    def _get_outputs(self) -> List[str]:
        """Returns the output names in list form.
        """
        raise NotImplementedError()
