import abc
import os
import csv
from typing import List, Dict, Final

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.generator.single_run_generator_node import SingleRunGeneratorNode


class CSVFile(SingleRunGeneratorNode):
    """Node that reads data from a CSV file and sends it to its outputs. It can be used to read data from a file
    and send it to a processing pipeline.
    
    When the node is initialized, it reads the CSV file and stores its data in memory(FrameworkData class). When the node is executed, it
    sends the data to its outputs.
    
    If you want to use this node in your pipeline, you must define the following parameters in the pipeline configuration.json file:

        **name** (*str*): Node name.\n
        **module** (*str*): Current module name (in this case ``models.node.generator.file.csvfile``).\n
        **type** (*str*): Current node type (in this case ``CSVFile``).\n
        **file_path** (*str*): Path to the CSV file.\n
        **sampling_frequency** (*float*): The sample frequency used to collect the data in the CSV file.\n
        **timestamp_column_name** (*str, optional*): Name of the column that contains the timestamp data.\n
        **channel_column_names** (*List[str], optional*): List of column names of the channels that will be read from the CSV file.\n
        **buffer_options** (*dict*): Buffer options.
            **clear_output_buffer_on_generate** (*bool*): If ``True``, the output buffer will be cleared when the node is executed.\n    
        **outputs** (*dict*): Dictionary containing the node outputs. Where you want to send the data read from the CSV file to, in other words, the next node in the pipeline.\n
    """
    
    _MODULE_NAME: Final[str] = 'node.generator.file.csvfile'

    OUTPUT_MAIN: Final[str] = 'main'
    OUTPUT_TIMESTAMP: Final[str] = 'timestamp'

    def _validate_parameters(self, parameters: dict):
        """This method validates the parameters passed to this node. It checks if the required parameters are present and if they have the correct type.

        :param parameters: Parameters passed to this node.
        :type parameters: dict

        :raises MissingParameterError: If a required parameter is missing.
        :raises InvalidParameterValue: If a parameter has an invalid value.
        """
        if 'sampling_frequency' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME,name=self.name,
                                        parameter='sampling_frequency')
        if 'file_path' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME,name=self.name,
                                        parameter='file_path')
        if type(parameters['sampling_frequency']) is not float and type(parameters['sampling_frequency']) is not int:
            raise InvalidParameterValue(module=self._MODULE_NAME,name=self.name,
                                        parameter='sampling_frequency',
                                        cause='must_be_number')
        if type(parameters['file_path']) is not str:
            raise InvalidParameterValue(module=self._MODULE_NAME,name=self.name,
                                        parameter='file_path',
                                        cause='must_be_string')
        if os.path.splitext(parameters['file_path'])[1] != '.csv':
            raise InvalidParameterValue(module=self._MODULE_NAME,name=self.name,
                                        parameter='file_path',
                                        cause='must_be_csv_file')
        if not os.path.exists(parameters['file_path']):
            raise InvalidParameterValue(module=self._MODULE_NAME,name=self.name,
                                        parameter='file_path',
                                        cause='file_doesnt_exist')
        if 'timestamp_column_name' in parameters and type(parameters['timestamp_column_name']) is not str:
            raise InvalidParameterValue(module=self._MODULE_NAME,name=self.name,
                                        parameter='timestamp_column_name',
                                        cause='must_be_string')

        if 'channel_column_names' in parameters:
            if type(parameters['channel_column_names']) is not list:
                raise InvalidParameterValue(module=self._MODULE_NAME,name=self.name,
                                            parameter='channel_column_names',
                                            cause='must_be_list')
            if len(parameters['channel_column_names']) < 1:
                raise InvalidParameterValue(module=self._MODULE_NAME,name=self.name,
                                            parameter='channel_column_names',
                                            cause='is_empty')
            if any(type(element) is not str for element in parameters['channel_column_names']):
                raise InvalidParameterValue(module=self._MODULE_NAME,name=self.name,
                                            parameter='channel_column_names',
                                            cause='must_contain_strings_only')

    @abc.abstractmethod
    def _initialize_parameter_fields(self, parameters: dict):
        """This method initializes the parameters of this node.

        :param parameters: Parameters passed to this node.
        :type parameters: dict
        """
        super()._initialize_parameter_fields(parameters)
        self.sampling_frequency = parameters['sampling_frequency']
        self.file_path = parameters['file_path']
        self.channel_column_names = parameters['channel_column_names'] \
            if 'channel_column_names' in parameters \
            else None
        self.timestamp_column_name = parameters['timestamp_column_name'] \
            if 'timestamp_column_name' in parameters \
            else None

    def _init_csv_reader(self) -> None:
        """This method initializes the CSV reader object. It opens the CSV file and creates a CSV reader object that will be used to read the file.
        """
        self.print(f'{self.file_path} opened')
        self._csv_file = open(self.file_path)
        self._csv_reader = csv.DictReader(self._csv_file)

    def _should_generate_timestamp(self) -> bool:
        return self.timestamp_column_name is None

    def _is_next_node_call_enabled(self) -> bool:
        return self._output_buffer[self.OUTPUT_TIMESTAMP].has_data()

    def _is_generate_data_condition_satisfied(self) -> bool:
        return True

    def _generate_data(self) -> Dict[str, FrameworkData]:
        """This method reads the csv file and store the data in a FrameworkData object.
        """
        self._init_csv_reader()
        main_data = FrameworkData(self.sampling_frequency, self.channel_column_names)
        timestamp_data = FrameworkData(self.sampling_frequency)
        for row_index, row in enumerate(self._csv_reader):
            if row_index == 0 and self.channel_column_names is None:
                self.channel_column_names = row.keys()
            for channel_name in self.channel_column_names:
                main_data.input_data_on_channel([float(row[channel_name])], channel_name)
            row_timestamp = row_index if self._should_generate_timestamp() else row[self.timestamp_column_name]
            timestamp_data.input_data_on_channel(data=[row_timestamp])
        self._csv_file.close()

        self.print(f'{self.file_path} closed')
        return {
            self.OUTPUT_MAIN: main_data,
            self.OUTPUT_TIMESTAMP: timestamp_data
        }

    def _get_outputs(self) -> List[str]:
        """This method returns the outputs of this node.

        :return: List of outputs of this node.
        :rtype: List[str]
        """
        return [
            self.OUTPUT_MAIN,
            self.OUTPUT_TIMESTAMP
        ]

    def dispose(self) -> None:
        self._clear_output_buffer()
        self._clear_input_buffer()
        if self._csv_file is not None and not self._csv_file.closed:
            self._csv_file.close()
