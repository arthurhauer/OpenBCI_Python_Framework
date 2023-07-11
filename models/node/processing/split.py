import abc
from typing import List, Dict, Final

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode


class Split(ProcessingNode):
    """ This node splits channels from ``FrameworkData``, using a user-provided split list.
        In the example below, the node is named 'split', and it splits the input data channels 'Fz' and 'marker'
        to dynamically set outputs 'data' and 'label'. Then, it outputs the split data to a node named 'csp'

    .. code-block::

        "split": {
                "module": "models.node.processing",
                "type": "Split",
                "split": {
                  "data": [
                    "Fz"
                  ],
                  "label": [
                    "marker"
                  ]
                },
                "buffer_options": {
                  "clear_output_buffer_on_data_input": true,
                  "clear_input_buffer_after_process": true,
                  "clear_output_buffer_after_process": true
                },
                "outputs": {
                  "data": [
                    {
                      "node": "csp",
                      "input": "data"
                    }
                  ],
                  "label": [
                    {
                      "node": "csp",
                      "input": "label"
                    }
                  ]
                }
              }

    ``configuration.json`` usage:
        **module** (*str*): Current module name (in this case ``models.node.processing``).\n
        **type** (*str*): Current node type (in this case ``Merge``).\n
        **split** (*dict*): Dictionary for channel splitting. Given keys will be the node's outputs.
        Each key value must be a list of strings, containing existing input data channel names.\n
        **buffer_options** (*dict*): Buffer options:
            **clear_output_buffer_on_data_input** (*bool*): If ``True``, the output buffer will be cleared when data is inputted.\n
            **clear_input_buffer_after_process** (*bool*): If ``True``, the input buffer will be cleared after the node is executed.\n
            **clear_output_buffer_after_process** (*bool*): If ``True``, the output buffer will be cleared after the node is executed.\n
    """
    _MODULE_NAME: Final[str] = 'node.processing.split'

    INPUT_MAIN: Final[str] = 'main'

    @abc.abstractmethod
    def _validate_parameters(self, parameters: dict):
        """Validates the parameters that were passed to the node. In this case it calls the parent method and validates the 'split' parameter format.
        """
        super()._validate_parameters(parameters)
        if 'split' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='split')
        if type(parameters['split']) is not dict:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='split',
                                        cause='must_be_dict')
        if len(parameters['split']) < 2:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='split',
                                        cause='must_be_have_at_least_2_keys')
        for key in parameters['split']:
            if type(parameters['split'][key]) is not list:
                raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                            parameter=f'split.{key}',
                                            cause='must_be_list')
            if len(parameters['split'][key]) < 1:
                raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                            parameter=f'split.{key}',
                                            cause='must_not_be_empty')
            for channel in parameters['split'][key]:
                if type(channel) is not str:
                    raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                                parameter=f'split.{key}.{channel}',
                                                cause='must_be_str')

    @abc.abstractmethod
    def _initialize_parameter_fields(self, parameters: dict):
        """Initializes the parameters that were passed to the node. In this case it calls the parent method,
        dynamically initializes the outputs, and initializes the split configuration object.
        """
        super()._initialize_parameter_fields(parameters)
        self._outputs: List[str] = list(parameters['split'].keys())
        self._split: Dict[str, List[str]] = parameters['split']

    def _is_next_node_call_enabled(self) -> bool:
        """ This method will return ``True`` if the next node call is enabled. This method will always return ``True``
        because the next node call is always enabled.
        """
        return True

    def _is_processing_condition_satisfied(self) -> bool:
        """ This method will return ``True`` if the processing condition is satisfied. This method will return ``True``
        if the input buffer has data in the configured split channels.

        :return: ``True`` if the input buffer has data in configured channels, ``False`` otherwise.
        :rtype: bool
        """
        condition: bool = True
        for key in self._split:
            for channel in self._split[key]:
                condition = condition and  channel in self._input_buffer[self.INPUT_MAIN].channels
                if not condition:
                    break
                condition = condition and len(self._input_buffer[self.INPUT_MAIN].get_data_on_channel(channel)) > 0

        return condition

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        """ This method processes the data that was inputted to the node. It splits the channels according to the 'split' parameter.

        :param data: The data that was inputted to the node.
        :type data: Dict[str, FrameworkData]

        :return: The renamed data.
        :rtype: Dict[str, FrameworkData]
        """
        input_data = data[self.INPUT_MAIN]
        return_dict: Dict[str, FrameworkData] = {}
        for key in self._split:
            channels: List[str] = self._split[key]
            return_dict[key] = FrameworkData(input_data.sampling_frequency, channels)
            for channel in channels:
                return_dict[key].input_data_on_channel(input_data.get_data_on_channel(channel), channel)
        return return_dict

    def _get_inputs(self) -> List[str]:
        """ This method will return the inputs of the node.

        :return: The inputs of the node.
        :rtype: list
        """
        return [
            self.INPUT_MAIN
        ]

    def _get_outputs(self) -> List[str]:
        """ This method will return the outputs of the node.

        :return: The outputs of the node.
        :rtype: list
        """
        return self._outputs
