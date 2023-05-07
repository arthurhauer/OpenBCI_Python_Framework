import csv
import os
from typing import List, Final

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.output.output_node import OutputNode


class CSVFile(OutputNode):
    _MODULE_NAME: Final[str] = 'node.output.file.csvfile'

    INPUT_MAIN: Final[str] = 'main'

    def _validate_parameters(self, parameters: dict):
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
        super()._initialize_parameter_fields(parameters)
        self.file_path = parameters['file_path']
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
            # self.file_path = f'{self.file_path[:-4]}_{int(time.time() * 1000)}.csv'
        self._csv_file = None

    def _get_inputs(self) -> List[str]:
        return [
            self.INPUT_MAIN
        ]

    def _init_csv_writer(self, data: FrameworkData) -> None:
        if self._csv_file is None:
            if not os.path.exists('\\'.join(self.file_path.split('\\')[0:-1])):
                os.makedirs('\\'.join(self.file_path.split('\\')[0:-1]))
            self.print('Creating csv file')
            self._csv_file = open(self.file_path, "w", newline='')
            self._csv_writer = csv.writer(self._csv_file)
            self._channels = None

    def _write_csv_columns(self, channels: List[str]) -> None:
        if self._channels is not None:
            return

        if len(channels) == 0:
            return

        self._channels = channels
        self.print('Writing columns')
        self._csv_writer.writerow(self._channels)

    def _write_data(self, data: FrameworkData) -> None:
        self.print(f'Writing data to file')
        formatted_data = zip(*data.get_data().values())
        self._csv_writer.writerows(formatted_data)
        self.print(f'Done')

    def _run(self, data: FrameworkData, input_name: str) -> None:
        self._init_csv_writer(data)
        self._write_csv_columns(data.channels)
        self._write_data(data)
        self._csv_file.flush()

    def dispose(self) -> None:
        self._clear_output_buffer()
        self._clear_input_buffer()
        if self._csv_file is not None and not self._csv_file.closed:
            self._csv_file.close()
            self._csv_file = None
