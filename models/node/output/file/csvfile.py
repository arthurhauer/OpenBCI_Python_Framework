import csv
import os
from typing import List, Final

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.output.output_node import OutputNode


class CSVFile(OutputNode):
    """ This node is capable of creating/writing the output data to a CSV file. 

    Attributes:
        _MODULE_NAME (str): The name of this module (in this case, 'node.output.file.csvfile').
        INPUT_MAIN (str): The name of the main input (in this case, 'main').
    
    ``configuration.json`` usage example:

        **module**: Current module name (in this case ``models.node.output.file``).\n
        **name**: Current node instance name (in this case, ``CSVFile``).\n
        **file_path** (str): The path to the CSV file that will be created/written to.\n
        **buffer_options** (dict): The buffer options.\n
            **clear_output_buffer_on_data_input** (bool): Whether to clear the output buffer when data is inputted.\n
            **clear_input_buffer_after_process** (bool): Whether to clear the input buffer after the process method is called.\n
            **clear_output_buffer_after_process** (bool): Whether to clear the output buffer after the process method is called.\n
    """
    _MODULE_NAME: Final[str] = 'node.output.file.csvfile'

    INPUT_MAIN: Final[str] = 'main'

    def _validate_parameters(self, parameters: dict):
        """ Validates the parameters that were passed to the node.

        :param parameters: The parameters that were passed to the node.
        :type parameters: dict

        :raises MissingParameterError: The ``file_path`` parameter is required.
        :raises InvalidParameterValue: The ``file_path`` parameter must be a string.
        :raises InvalidParameterValue: The ``file_path`` parameter must be a CSV file.

        """
        if 'file_path' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='file_path')
        if type(parameters['file_path']) is not str:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='file_path',
                                        cause='must_be_string')
        if os.path.splitext(parameters['file_path'])[1] != '.csv':
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='file_path',
                                        cause='must_be_csv_file')

    def _initialize_parameter_fields(self, parameters: dict):
        """ Initializes the parameters that were passed to the node.

        :param parameters: The parameters that were passed to the node.
        :type parameters: dict
        """
        super()._initialize_parameter_fields(parameters)
        self.file_path = parameters['file_path']
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
            # self.file_path = f'{self.file_path[:-4]}_{int(time.time() * 1000)}.csv'
        self._csv_file = None

    def _get_inputs(self) -> List[str]:
        """ Returns the input names of this node.
        """
        return [
            self.INPUT_MAIN
        ]

    def _init_csv_writer(self, data: FrameworkData) -> None:
        """ Initializes the CSV writer.
        """
        if self._csv_file is None:
            if not os.path.exists('\\'.join(self.file_path.split('\\')[0:-1])):
                os.makedirs('\\'.join(self.file_path.split('\\')[0:-1]))
            self.print('Creating csv file')
            self._csv_file = open(self.file_path, "w", newline='')
            self._csv_writer = csv.writer(self._csv_file)
            self._channels = None

    def _write_csv_columns(self, channels: List[str]) -> None:
        """ Writes the CSV columns labels.

        :param channels: The channels to write.
        :type channels: List[str]
        """
        if self._channels is not None:
            return

        if len(channels) == 0:
            return

        self._channels = channels
        self.print('Writing columns')
        self._csv_writer.writerow(self._channels)

    def _write_data(self, data: FrameworkData) -> None:
        """ Writes the data to the CSV file.

        :param data: The data to write.
        :type data: FrameworkData
        """
        self.print(f'Writing data to file')
        formatted_data = zip(*data.get_data().values())
        self._csv_writer.writerows(formatted_data)
        self.print(f'Done')

    def _run(self, data: FrameworkData, input_name: str) -> None:
        """ Runs the node.
        """
        self._init_csv_writer(data)
        self._write_csv_columns(data.channels)
        self._write_data(data)
        self._csv_file.flush()

    def dispose(self) -> None:
        """ Node self implementation of disposal of allocated resources.
        """
        self._clear_output_buffer()
        self._clear_input_buffer()
        if self._csv_file is not None and not self._csv_file.closed:
            self._csv_file.close()
            self._csv_file = None
