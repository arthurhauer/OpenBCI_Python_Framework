from typing import Dict, List, Final
import numpy as np
from scipy.signal import convolve, get_window

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode

class Smoothing(ProcessingNode):
    """
    A processing node that smooths input data by convolving each channel with a window function.

    Attributes:
        _MODULE_NAME (str): The name of the module (``node.processing.smoothing``).
        INPUT_MAIN (str): The key for the main input data.
        OUTPUT_MAIN (str): The key for the main output data.
        _window_type (str): The type of window function used for convolution.
        _window_size (int): The size of the window function.
        _convolution_mode (str): The mode of convolution.
        _window (np.ndarray): The window function used for convolution.

    Methods:
        __init__(parameters: dict): Initializes the node with the given parameters.
        _validate_parameters(parameters: dict): Validates the parameters passed to this node.
        _initialize_parameter_fields(parameters: dict): Initializes the parameter fields of this node.
        _is_next_node_call_enabled() -> bool: Determines if the next node call is enabled.
        _is_processing_condition_satisfied() -> bool: Checks if the processing condition is satisfied.
        _process(data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]: Smooths the input data.
        _get_inputs() -> List[str]: Returns the list of input keys.
        _get_outputs() -> List[str]: Returns the list of output keys.

    Parameters:
        parameters (dict): A dictionary containing the parameters for the node.
            - window_type (str): The type of window function to use. Must be one of the following:
                'boxcar', 'triang', 'blackman', 'hamming', 'hann', 'bartlett', 'flattop', 'parzen', 'bohman',
                'blackmanharris', 'nuttall', 'barthann', 'cosine', 'exponential', 'tukey', 'taylor', 'lanczos'.
            - window_size (int): The size of the window function. Must be a positive integer.
            - convolution_mode (str): The mode of convolution. Must be one of the following: 'full', 'valid', 'same'.

    Example JSON:
    {
        "module": "models.node.processing.smoothing",
        "type": "Smoothing",
        "window_type": "hann",
        "window_size": 5,
        "convolution_mode": "same",
        "outputs": {
            "main": []
        },
        "buffer_options": {
            "clear_output_buffer_on_data_input": true,
            "clear_input_buffer_after_process": false,
            "clear_output_buffer_after_process": false
        }
    }
    """

    _MODULE_NAME: Final[str] = 'node.processing.smoothing'
    INPUT_MAIN: Final[str] = 'main'
    OUTPUT_MAIN: Final[str] = 'main'

    def _validate_parameters(self, parameters: dict):
        """ Validates the parameters passed to this node. """
        super()._validate_parameters(parameters)
        if 'window_type' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name, parameter='window_type')
        if 'window_size' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name, parameter='window_size')
        if 'convolution_mode' not in parameters:
            parameters['convolution_mode'] = 'full'
        if type(parameters['window_type']) is not str:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name, parameter='window_type', cause='must_be_str')
        if type(parameters['window_size']) is not int or parameters['window_size'] < 1:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name, parameter='window_size', cause='must_be_positive_int')
        if type(parameters['convolution_mode']) is not str:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name, parameter='convolution_mode', cause='must_be_str')
        valid_window_types = [
            'boxcar', 'triang', 'blackman', 'hamming', 'hann', 'bartlett', 'flattop', 'parzen', 'bohman',
            'blackmanharris', 'nuttall', 'barthann', 'cosine', 'exponential', 'tukey', 'taylor', 'lanczos'
        ]
        if parameters['window_type'] not in valid_window_types:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name, parameter='window_type', cause='invalid_value')

        # Validate convolution_mode
        valid_modes = ['full', 'valid', 'same']
        if parameters['convolution_mode'] not in valid_modes:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name, parameter='convolution_mode', cause='invalid_value')

    def _initialize_parameter_fields(self, parameters: dict):
        """ Initializes the parameter fields of this node. """
        super()._initialize_parameter_fields(parameters)
        self._window_type = parameters['window_type']
        self._window_size = parameters['window_size']
        self._convolution_mode = parameters['convolution_mode']
        self._window = get_window(self._window_type, self._window_size)

    def _is_next_node_call_enabled(self) -> bool:
        """ Determines if the next node call is enabled. """
        return self._output_buffer[self.OUTPUT_MAIN].get_data_count() > 0

    def _is_processing_condition_satisfied(self) -> bool:
        """ Checks if the processing condition is satisfied. """
        return self._input_buffer[self.INPUT_MAIN].get_data_count() > 0

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        """ Smooths the input data by convolving each channel with the window function. """
        smoothed_data: Dict[str, FrameworkData] = {}
        for key in data:
            smoothed_data[key] = FrameworkData(sampling_frequency_hz=data[key].sampling_frequency, channels=data[key].channels)
            for channel in data[key].channels:
                raw_signal = data[key].get_data_on_channel(channel)
                smoothed_signal = convolve(raw_signal, self._window, mode=self._convolution_mode)[0:len(raw_signal)]
                log_smooth = np.log(smoothed_signal)
                smoothed_data[key].input_data_on_channel(log_smooth, channel)
        return smoothed_data

    def _get_inputs(self) -> List[str]:
        """ Returns the list of input keys. """
        return [self.INPUT_MAIN]

    def _get_outputs(self) -> List[str]:
        """ Returns the list of output keys. """
        return [self.OUTPUT_MAIN]