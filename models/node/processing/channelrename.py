from typing import List, Dict, Final

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode


class ChannelRename(ProcessingNode):
    """ This node simply renames channels from ``FrameworkData``, using a user-provided dictionary for conversion.
        In the example below, the node is named 'rename', and it renames the input channel 'main' to 'marker'.
        Afterwards, it outputs the converted data to a node named 'merge', in its 'slave_main' input.

    .. code-block::

        "rename": {
            "module": "models.node.processing",
            "type": "ChannelRename",
            "dictionary": {
                "main": "marker"
            },
            "buffer_options": {
                "clear_output_buffer_on_data_input": true,
                "clear_input_buffer_after_process": true,
                "clear_output_buffer_after_process": true
            },
            "outputs": {
                "main": [
                    {
                        "node": "merge",
                        "input": "slave_main"
                    }
                ]
            }
        }

    Attributes:
        _MODULE_NAME (str): The name of the module(in this case ``node.processing.channelrename``)
        INPUT_MAIN (str): The name of the main input(in this case ``main``)
        OUTPUT_MAIN (str): The name of the main output(in this case ``main``)

    ``configuration.json`` usage:
        **module** (*str*): Current module name (in this case ``models.node.processing``).\n
        **type** (*str*): Current node type (in this case ``Merge``).\n
        **dictionary** (*dict*): Dictionary for channel name conversion. Keys provided must be existing channels in the node's input buffer.
        **buffer_options** (*dict*): Buffer options:
            **clear_output_buffer_on_data_input** (*bool*): If ``True``, the output buffer will be cleared when data is inputted.\n
            **clear_input_buffer_after_process** (*bool*): If ``True``, the input buffer will be cleared after the node is executed.\n
            **clear_output_buffer_after_process** (*bool*): If ``True``, the output buffer will be cleared after the node is executed.\n
    """
    _MODULE_NAME: Final[str] = 'node.processing.channelrename'

    INPUT_MAIN: Final[str] = 'main'
    OUTPUT_MAIN: Final[str] = 'main'

    def _validate_parameters(self, parameters: dict):
        """Validates the parameters that were passed to the node. In this case it calls the parent method and validates the 'dictionary' parameter format.
        """
        super()._validate_parameters(parameters)
        if 'dictionary' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='dictionary')
        if type(parameters['dictionary']) is not dict:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='split',
                                        cause='must_be_dict')
        if len(parameters['dictionary']) < 1:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='split',
                                        cause='must_be_have_at_least_1_key')
        for key in parameters['dictionary']:
            if type(key) is not str:
                raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                            parameter=f'split.{key}',
                                            cause='key_must_be_str')
            if type(parameters['dictionary'][key]) is not str:
                raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                            parameter=f'split.{key}',
                                            cause='value_must_be_str')

    def _initialize_parameter_fields(self, parameters: dict):
        """Initializes the parameters that were passed to the node. In this case it calls the parent method and initializes the renaming dictionary for data processing.
        """
        super()._initialize_parameter_fields(parameters)
        self._rename_dictionary: Dict[str, str] = parameters['dictionary']

    def _is_next_node_call_enabled(self) -> bool:
        """ This method allows the next node call. In this case it enables whenever there's data in the output buffer.
        """
        return self._output_buffer[self.OUTPUT_MAIN].get_data_count() > 0

    def _is_processing_condition_satisfied(self) -> bool:
        """ This method will return ``True`` if the processing condition is satisfied. This method will return ``True``
        if the input buffer has data.

        :return: ``True`` if the input buffer has data, ``False`` otherwise.
        :rtype: bool
        """
        return self._input_buffer[self.INPUT_MAIN].get_data_count() > 0

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        """ This method processes the data that was inputted to the node. It renames the input data channels based on a user given renaming dictionary.

        :param data: The data that was inputted to the node.
        :type data: Dict[str, FrameworkData]

        :return: The renamed data.
        :rtype: Dict[str, FrameworkData]
        """
        renamed_data = data[self.INPUT_MAIN]
        for key in self._rename_dictionary:
            renamed_data.rename_channel(key, self._rename_dictionary[key])
        return {
            self.OUTPUT_MAIN: renamed_data
        }

    def _get_inputs(self) -> List[str]:
        """ This method returns the inputs of the node. In this case it returns a single 'main' input.
        """
        return [
            self.INPUT_MAIN
        ]

    def _get_outputs(self) -> List[str]:
        """ This method returns the outputs of the node. In this case it returns a single 'main' output.
        """
        return [
            self.OUTPUT_MAIN
        ]
