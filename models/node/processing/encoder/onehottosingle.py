import abc
from typing import Final, Dict

import numpy as np

from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode
from typing import List


class OneHotToSingle(ProcessingNode):
    """ Converts a one-hot encoded signal to a single channel signal. 
    One-hot encoded signals are signals where each label is represented by a vector of the same length as the number 
    of labels, where the label is represented by a 1 at the index of the label and 0 everywhere else. 
    A Single channel signal is a signal where each label is represented by a single channel, where the label is
    represented by the index.
    This node converts a one-hot encoded labels to a single channel label. The single label count starts at 1, so the
    label 1 is represented by the channel 1, the label 2 by the channel 2, etc. There is no label 0.

    Attributes:
        _MODULE_NAME (`str`): The name of the module (in his case ``node.processing.encoder.onehottosingle``)
        INPUT_MAIN (`str`): The name of the main input signal (in this case ``main``)
        OUTPUT_MAIN (`str`): The name of the main output signal (in this case ``main``)

    configuration.json usage:
        **module** (*str*): The name of the module (``node.processing.encoder``)\n
        **type** (*str*): The type of the node (``OneHotToSingle``)\n
        **buffer_options** (*dict*): Buffer options.\n
            **clear_output_buffer_on_data_input** (*bool*): Whether to clear the output buffer when new data is inserted in the input buffer.\n
            **clear_input_buffer_after_process** (*bool*): Whether to clear the input buffer after processing.\n
            **clear_output_buffer_after_process** (*bool*): Whether to clear the output buffer after processing.\n

    """
    _MODULE_NAME: Final[str] = 'node.processing.encoder.onehottosingle'

    INPUT_MAIN: Final[str] = 'main'
    OUTPUT_MAIN: Final[str] = 'main'

    @abc.abstractmethod
    def _initialize_parameter_fields(self, parameters: dict):
        """ Initializes the parameter fields of this node.

        :param parameters: The parameters passed to this node.
        :type parameters: dict
        """
        super()._initialize_parameter_fields(parameters)

    def _is_next_node_call_enabled(self) -> bool:
        """ Returns whether the next node call is enabled. The next node call is enabled if the input buffer is not empty.
        """
        return self._output_buffer[self.OUTPUT_MAIN].get_data_count() > 0

    def _is_processing_condition_satisfied(self) -> bool:
        """ Returns whether the processing condition is satisfied. The processing condition is satisfied if the input buffer is not empty.
        """
        return self._input_buffer[self.INPUT_MAIN].get_data_count() > 0

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        """ This method encodes the data labels that before was one-hot encoded to a single channel labels. It does this
        by finding the index of the channel that has a value of 1 and then setting the output channel to that index + 1. It 
        does this for each data point in the dataset.

        :param data: The data to process.
        :type data: dict[str, FrameworkData]

        :return: The processed data.
        :rtype: dict[str, FrameworkData]
        """
        self.print('encoding...')
        raw_data = data[self.INPUT_MAIN]
        encoded_data: FrameworkData = FrameworkData(sampling_frequency_hz=raw_data.sampling_frequency)
        encoded = np.argmax(raw_data.get_data_as_2d_array(), axis=0)
        encoded_data.input_data_on_channel(encoded)
        self.print('encoded!')
        return {
            self.OUTPUT_MAIN: encoded_data
        }

    def _get_inputs(self) -> List[str]:
        """ Returns the inputs of this node.
        """
        return [
            self.INPUT_MAIN
        ]

    def _get_outputs(self) -> List[str]:
        """ Returns the outputs of this node.
        """
        return [
            self.OUTPUT_MAIN
        ]
