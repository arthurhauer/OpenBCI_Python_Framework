import abc
from typing import Final, Dict

from models.exception.non_compatible_data import NonCompatibleData
from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode
from typing import List


class SingleToOneHot(ProcessingNode):
    """ Converts a single channel encoding (Ordinal encoding) signal to a one-hot encoding.
    One-hot encoded signals are signals where each label is represented by a vector of the same length as the number 
    of labels, where the label is represented by a 1 at the index of the label and 0 everywhere else. 
    A Single channel encoded (Ordinal encoding) signal is a type of signal where each label is represented by a number,
    where the label is represented by the index of the label.
    This node converts a single channel labels to a one-hot encoded label. The single label count starts at 1, so the
    label 1 is represented by the channel 1, the label 2 by the channel 2, etc. There is no label 0.

    Attributes:
        _MODULE_NAME (`str`): The name of the module (in his case ``node.processing.encoder.singletoonehot``)
        INPUT_MAIN (`str`): The name of the main input signal (in this case ``main``)
        OUTPUT_MAIN (`str`): The name of the main output signal (in this case ``main``)

    configuration.json usage:
        **module** (*str*): The name of the module (``node.processing.encoder``)\n
        **type** (*str*): The type of the node (``SingleToOneHot``)\n
        **buffer_options** (*dict*): Buffer options.\n
            **clear_output_buffer_on_data_input** (*bool*): Whether to clear the output buffer when new data is inserted in the input buffer.\n
            **clear_input_buffer_after_process** (*bool*): Whether to clear the input buffer after processing.\n
            **clear_output_buffer_after_process** (*bool*): Whether to clear the output buffer after processing.\n
    """
    _MODULE_NAME: Final[str] = 'node.processing.encoder.singletoonehot'

    INPUT_MAIN: Final[str] = 'main'
    OUTPUT_MAIN: Final[str] = 'main'

    @abc.abstractmethod
    def _initialize_parameter_fields(self, parameters: dict):
        """ Initializes the parameter fields of this node.

        :param parameters: The parameters passed to this node.
        :type parameters: dict
        """
        super()._initialize_parameter_fields(parameters)
        self.labels = parameters['labels']

    def _is_next_node_call_enabled(self) -> bool:
        """ Returns whether the next node call is enabled. The next node call is enabled if the input buffer is not empty.
        """
        return self._output_buffer[self.OUTPUT_MAIN].get_data_count() > 0

    def _is_processing_condition_satisfied(self) -> bool:
        """ Returns whether the processing condition is satisfied. The processing condition is satisfied if the input buffer is not empty.
        """
        return self._input_buffer[self.INPUT_MAIN].get_data_count() > 0

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        """ This method encodes the data labels that before was a single channel label (Ordinal encoding) to a one-hot encoded label. It does this
        comparing the index of the channel to the label and setting the output channel to 1 if the index is equal to the label and 0 otherwise. It
        does this for each data point in the dataset.

        :param data: The data to process.
        :type data: dict

        :return: The processed data.
        :rtype: dict
        """
        self.print('encoding...')
        raw_data = data[self.INPUT_MAIN]
        if not raw_data.is_1d():
            raise NonCompatibleData(module=self._MODULE_NAME,name=self.name, cause='provided_data_is_multichannel')

        encoded_data: FrameworkData = FrameworkData(sampling_frequency_hz=raw_data.sampling_frequency,
                                                    channels=self.labels)
        for data_entry in raw_data.get_data_single_channel():
            for channel_index, channel in enumerate(self.labels):
                encoded_value = 1 if channel_index == data_entry-1 else 0
                encoded_data.input_data_on_channel([encoded_value], channel)
        self.print('encoded!')
        return {
            self.OUTPUT_MAIN: encoded_data
        }

    def _get_inputs(self) -> List[str]:
        """ Returns the input fields of this node.
        """
        return [
            self.INPUT_MAIN
        ]

    def _get_outputs(self) -> List[str]:
        """ Returns the output fields of this node.
        """
        return [
            self.OUTPUT_MAIN
        ]
