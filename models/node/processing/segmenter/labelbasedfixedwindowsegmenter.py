from typing import Final, List, Dict

import numpy as np

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.processing.segmenter.segmenter import Segmenter


class LabelBasedFixedWindowSegmenter(Segmenter):
    """
    Segments the input data into fixed-size windows based on the occurrence of a specified label. Each window is a list of samples,
    typically called an epoch. This segmentation is crucial for subsequent nodes in the processing pipeline, such as feature extractors,
    which expect data to be segmented in this manner.

    Attributes:
        _MODULE_NAME (str): The name of the module (``node.processing.segmenter.labelbasedfixedwindowsegmenter``).
        INPUT_DATA (str): The key for input data.
        INPUT_LABEL (str): The key for input labels.
        OUTPUT_DATA (str): The key for output data.
        OUTPUT_LABEL (str): The key for output labels.
        _label_value (int): The label value used to trigger segmentation.
        _samples_after_label (int): The number of samples to include after the label.
        _samples_before_label (int): The number of samples to include before the label.
        _total_window_size (int): The total size of the window (samples before + samples after).

    Methods:
        __init__(parameters: dict): Initializes the segmenter with the given parameters.
        _is_processing_condition_satisfied() -> bool: Checks if there is enough data in the input buffer to create a window.
        _validate_parameters(parameters: dict): Validates the parameters passed to the segmenter.
        _process(data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]: Segments the input data into fixed-size windows based on the label.
        _get_inputs() -> List[str]: Returns the list of input keys.
        _get_outputs() -> List[str]: Returns the list of output keys.

    configuration.json usage:
        **module** (*str*): The name of the module (``models.node.processing.segmenter``)\n
        **type** (*str*): The type of the node (``LabelBasedFixedWindowSegmenter``)\n
        **label_value** (*int*): The value of the label to segment the data.\n
        **samples_after_label** (*int*): The number of samples after the label to segment the data.\n
        **samples_before_label** (*int*): The number of samples before the label to segment the data.\n
        **buffer_options** (*dict*): Buffer options.\n
            **clear_output_buffer_on_data_input** (*bool*): Whether to clear the output buffer when new data is inserted in the input buffer.\n
            **clear_input_buffer_after_process** (*bool*): Whether to clear the input buffer after processing.\n
            **clear_output_buffer_after_process** (*bool*): Whether to clear the output buffer after processing.\n

    Example:
    ```json
    {
      "module": "models.node.processing.segmenter",
      "type": "LabelBasedFixedWindowSegmenter",
      "label_value": 1,
      "filling_value": "zero",
      "samples_after_label": 2,
      "samples_before_label": 3,
      "buffer_options": {
        "clear_output_buffer_on_data_input": true,
        "clear_input_buffer_after_process": false,
        "clear_output_buffer_after_process": false
      },
      "outputs":{
        "data": [],
        "label": []
      }
    }
    ```
    In this example, the LabelBasedFixedWindowSegmenter segments the input data into fixed-size windows based on the occurrence of the label value 1.
    The segmenter includes 2 samples after the label and 3 samples before the label in each window.
    This will produce a window of 5 samples for each occurrence of the label value 1 in the input data.
    If the input label data is [0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0], the segmented data will be:
    ```
    Segmented Data: [[0, 0, 0, 1, 1], [1, 0, 0, 1, 1]]
    It clears the output buffer when new data is inserted in the input buffer and does not clear the input or output buffer after processing.

    """

    _MODULE_NAME: Final[str] = 'node.processing.segmenter.labelbasedfixedwindowsegmenter'

    INPUT_DATA: Final[str] = 'data'
    INPUT_LABEL: Final[str] = 'label'

    OUTPUT_DATA: Final[str] = 'data'
    OUTPUT_LABEL: Final[str] = 'label'

    def __init__(self, parameters: dict):
        super().__init__(parameters)
        self._filling_value = parameters['filling_value']
        self._label_value = parameters['label_value']
        self._samples_after_label = parameters['samples_after_label']
        self._samples_before_label = parameters['samples_before_label']
        self._total_window_size = self._samples_after_label + self._samples_before_label

    def _is_processing_condition_satisfied(self) -> bool:
        """
        Returns whether the processing condition is satisfied. In this case, it returns True if there is enough data in the
        input buffer to create a window of the specified size.

        :return: True if there is enough data in the input buffer, False otherwise.
        :rtype: bool
        """

        return self._input_buffer[self.INPUT_DATA].get_data_count() >= self._total_window_size

    def _is_next_node_call_enabled(self) -> bool:
        """ Returns whether the next node call is enabled. It's enabled whenever there's data in the main output buffer.
        """
        return self._output_buffer[self.OUTPUT_DATA].get_data_count() > 0 and self._output_buffer[self.OUTPUT_LABEL].get_data_count() > 0

    def _validate_parameters(self, parameters: dict):
        """
        Validates the parameters passed to this node. This method checks if the required parameters are present and if they
        are of the correct type and value.

        :param parameters: The parameters passed to this node.
        :type parameters: dict

        :raises MissingParameterError: If the ``label_value``, ``filling_value``, ``samples_after_label``, or ``samples_before_label`` parameter is missing.
        :raises InvalidParameterValue: If the ``label_value``, ``samples_after_label``, or ``samples_before_label`` parameter is not an int.
        :raises InvalidParameterValue: If the ``samples_after_label`` or ``samples_before_label`` parameter is less than 1.
        :raises MissingParameterError: If the  parameter is missing.
        :raises InvalidParameterValue: If the ``filling_value`` parameter is not ``zero`` or ``latest``.
        """

        super()._validate_parameters(parameters)

        if 'label_value' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='label_value')
        if 'filling_value' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='filling_value')
        if 'samples_after_label' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='samples_after_label')
        if 'samples_before_label' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='samples_before_label')
        if type(parameters['label_value']) is not int:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='label_value',
                                        cause='must_be_int')
        if type(parameters['samples_after_label']) is not int:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='samples_after_label',
                                        cause='must_be_int')
        if parameters['samples_after_label'] < 0:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='samples_after_label',
                                        cause='must_be_natural_number')
        if type(parameters['samples_before_label']) is not int:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='samples_before_label',
                                        cause='must_be_int')
        if parameters['samples_before_label'] < 0:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='samples_before_label',
                                        cause='must_be_natural_number')
        if type(parameters['filling_value']) is not str:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='filling_value',
                                        cause='must_be_str')
        if parameters['filling_value'] not in ['zero', 'latest']:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='filling_value',
                                        cause='must_be_in.[zero, latest]')

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        """
        Segments the input data into fixed-size windows based on the occurrence of a specified label. This method iterates
        through the label data, and when the specified label value is found, it creates a window containing a specified number
        of samples before and after the label. If the label is repeated continuously, only one window is generated for the
        sequence.

        :param data: A dictionary containing the input data and label data as FrameworkData objects.
        :type data: Dict[str, FrameworkData]

        :return: A dictionary containing the segmented data and labels as FrameworkData objects.
        :rtype: Dict[str, FrameworkData]
        """

        segmented_data: Dict[str, FrameworkData] = {
            self.OUTPUT_DATA: FrameworkData(sampling_frequency_hz=data[self.INPUT_DATA].sampling_frequency, channels=data[self.INPUT_DATA].channels),
            self.OUTPUT_LABEL: FrameworkData(sampling_frequency_hz=data[self.INPUT_LABEL].sampling_frequency, channels=data[self.INPUT_LABEL].channels)
        }

        label_data = data[self.INPUT_LABEL].get_data_single_channel()
        input_data = np.array(data[self.INPUT_DATA].get_data_as_2d_array())
        in_label_sequence = False

        for i in range(len(label_data)):
            if label_data[i] == self._label_value:
                if not in_label_sequence:
                    in_label_sequence = True
                    start_index = i - self._samples_before_label
                    end_index = i + self._samples_after_label

                    if start_index < 0 or end_index > input_data.shape[1]:
                        if self._filling_value == 'zero':
                            window_data = np.zeros((input_data.shape[0], self._total_window_size))
                            window_label = np.zeros(self._total_window_size)
                        elif self._filling_value == 'latest':
                            window_data = np.full((input_data.shape[0], self._total_window_size), input_data[:, max(0, start_index)].reshape(-1, 1))
                            window_label = np.full(self._total_window_size, label_data[max(0, start_index)])

                        if start_index < 0:
                            # noinspection PyUnboundLocalVariable
                            window_data[:, -start_index:] = input_data[:, :end_index]
                            # noinspection PyUnboundLocalVariable
                            window_label[-start_index:] = label_data[:end_index]
                        else:
                            window_data[:, :input_data.shape[1] - start_index] = input_data[:, start_index:]
                            window_label[:input_data.shape[1] - start_index] = label_data[start_index:]
                    else:
                        window_data = input_data[:, start_index:end_index]
                        window_label = label_data[start_index:end_index]


                    segmented_data[self.OUTPUT_DATA].input_2d_data(np.expand_dims(window_data, axis=1))
                    segmented_data[self.OUTPUT_LABEL].input_data_on_channel([np.max(window_label)])
            else:
                in_label_sequence = False
        return segmented_data

    def _get_inputs(self) -> List[str]:
        """ Returns the inputs of this node.
        """
        return [
            self.INPUT_DATA,
            self.INPUT_LABEL
        ]

    def _get_outputs(self) -> List[str]:
        """ Returns the outputs of this node.
        """
        return [
            self.OUTPUT_DATA,
            self.OUTPUT_LABEL
        ]
