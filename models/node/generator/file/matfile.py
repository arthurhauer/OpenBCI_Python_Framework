from typing import List, Dict, Final, Any

import numpy
import numpy as np
import scipy.io

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.generator.single_run_generator_node import SingleRunGeneratorNode


class MatFile(SingleRunGeneratorNode):
    """Node that reads data from a .mat file and converts it to FrameworkData.

    When the node is initialized, it reads the .mat file and stores its data in memory. When the node is executed, it
    sends the data to its outputs.

    If you want to use this node in your pipeline, you must define the following parameters in the pipeline configuration.json file:

        **name** (*str*): Node name.\n
        **module** (*str*): Current module name (in this case ``models.node.generator.file.matfile``).\n
        **type** (*str*): Current node type (in this case ``MatFile``).\n
        **file_path** (*str*): Path to the .mat file.\n
        **outputs** (*dict*): Dictionary containing the node outputs. Where you want to send the data read from the .mat file to, in other words, the next node in the pipeline.\n

    {
    "name": "MatFile1",
    "module": "models.node.generator.file.matfile",
    "type": "MatFile",
    "file_path": "/path/to/your/matfile.mat",
    "outputs": {
        "main": "NextNode1",
        "timestamp": "NextNode2"
    }
}

    """
    _MODULE_NAME: Final[str] = 'node.generator.file.matfile'

    def _validate_parameters(self, parameters: dict):
        super()._validate_parameters(parameters)
        if 'sampling_frequency' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='sampling_frequency')
        if 'file_path' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='file_path')
        if type(parameters['sampling_frequency']) is not int:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='sampling_frequency',
                                        cause='must_be_int')
        if type(parameters['file_path']) is not str:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='file_path',
                                        cause='must_be_string')

    def _initialize_parameter_fields(self, parameters: dict):
        super()._initialize_parameter_fields(parameters)
        self.file_path = parameters['file_path']
        self.sampling_frequency = parameters['sampling_frequency']

    def _is_next_node_call_enabled(self) -> bool:
        return self._output_buffer[self._get_outputs()[0]].has_data()

    def _is_generate_data_condition_satisfied(self) -> bool:
        return True

    def _generate_data(self) -> Dict[str, FrameworkData]:
        raw_data = scipy.io.loadmat(self.file_path)
        converted_data: Dict[str, FrameworkData] = {}
        for key in raw_data.keys():
            converted_data[key] = self._convert_to_framework_data(raw_data[key])
        return converted_data

    def _get_outputs(self) -> List[str]:
        mat_data = scipy.io.loadmat(self.file_path)
        return list(mat_data.keys())

    def _convert_to_framework_data(self, data: Any) -> FrameworkData:
        wrapper = FrameworkData()
        if type(data) is numpy.ndarray and np.issubdtype(data[0][0].dtype, np.number):
            return FrameworkData.from_multi_channel(self.sampling_frequency, [f'channel_{i}' for i in range(data.shape[1])],
                                                    data.transpose(1, 0))
        return wrapper

    def dispose(self) -> None:
        self._clear_output_buffer()
        self._clear_input_buffer()
