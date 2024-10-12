from typing import List, Final, Dict

import sys
import time

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.framework_data import FrameworkData
from models.node.output.output_node import OutputNode


class Console(OutputNode):
    """ This node displays it's input in the console.
    {
         "module": "models.node.output.display",
         "type": "Console",
         "prefix": "Acuracia = ",
         "buffer_options": {
         },
         "outputs": {
             "main": []
         }
     }
    Attributes:
        _MODULE_NAME (str): The name of this module (in this case, 'node.output.file').
        INPUT_MAIN (str): The name of the main input (in this case, 'main').
    
    ``configuration.json`` usage example:

        **module**: Current module name (in this case ``models.node.output``).\n
        **name**: Current node instance name (in this case, ``Console``).\n
        **buffer_options** (dict): The buffer options.\n
            **clear_output_buffer_on_data_input** (bool): Whether to clear the output buffer when data is inputted.\n
            **clear_input_buffer_after_process** (bool): Whether to clear the input buffer after the process method is called.\n
            **clear_output_buffer_after_process** (bool): Whether to clear the output buffer after the process method is called.\n
    """


    _MODULE_NAME: Final[str] = 'node.output.file.console'

    INPUT_MAIN: Final[str] = 'main'

    def _validate_parameters(self, parameters: dict):
        """ Validates the parameters that were passed to the node.

        :param parameters: The parameters that were passed to the node.
        :type parameters: dict

        """
        super()._validate_parameters(parameters)
        if 'inplace' not in parameters:
            parameters['inplace'] = False

        if 'prefix' not in parameters:
            parameters['prefix'] = ''

        if type(parameters['prefix']) is not str:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='prefix',
                                        cause='must_be_str')

        if type(parameters['inplace']) is not bool:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='inplace',
                                        cause='must_be_bool')

    def _initialize_parameter_fields(self, parameters: dict):
        """ Initializes the parameters that were passed to the node.

        :param parameters: The parameters that were passed to the node.
        :type parameters: dict
        """
        super()._initialize_parameter_fields(parameters)
        self._prefix = parameters['prefix']
        self._inplace = parameters['inplace']

    def _get_inputs(self) -> List[str]:
        """ Returns the input names of this node.
        """
        return [
            self.INPUT_MAIN
        ]

    def _is_processing_condition_satisfied(self) -> bool:
        return True

    def _process(self, data: Dict[str, FrameworkData]) -> None:
        """ Runs the node.
        """
        output = ''
        input_data= data[self.INPUT_MAIN]
        for channel in input_data.channels:
            output += f'{time.time()} - {self._MODULE_NAME}.{self.name} - {channel}: {self._prefix}{input_data.get_data_on_channel(channel)}'
        print(output, end='\r' if self._inplace else '\n')
        sys.stdout.flush()
        self._clear_input_buffer()

    def dispose(self) -> None:
        """ Node self implementation of disposal of allocated resources.
        """
        self._clear_output_buffer()
        self._clear_input_buffer()
        super().dispose()
