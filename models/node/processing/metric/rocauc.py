from typing import List, Dict, Final

from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode
from sklearn import metrics
import numpy as np


class ROCAUC(ProcessingNode):
    """ This node calculates the ROC AUC score. The ROC AUC score is a measure of how well a classifier can distinguish between classes.
    It is calculated as the area under the receiver operating characteristic curve. The ROC AUC score is a value between 0 and 1, where 0
    means that the classifier is not able to distinguish between classes and 1 means that the classifier can perfectly distinguish between
    classes.
    The input to this node should be the predicted probabilities of the classifier and the actual labels. The predicted probabilities should
    be a 2D array where each row represents the predicted probabilities for a sample and each column represents the predicted probability
    for a class. The actual labels should be a 2D array where each row represents the actual labels for a sample, in a one-hot fashion.
    The predicted probabilities and actual labels should have the same number of samples.

    Attributes:
        _MODULE_NAME (str): The name of the module (``node.processing.metric.roc_auc``).
        INPUT_PREDICTED (str): The key for the predicted probabilities input data.
        INPUT_ACTUAL (str): The key for the actual labels input data.
        OUTPUT_MAIN (str): The key for the main output data.

    configuration.json usage:
        **module** (*str*): The name of the module (``models.node.processing.metric``)\n
        **type** (*str*): The name of the class (``ROCAUC``)\n
        **outputs** (*dict*): The outputs of the node.\n
            **main** (*list*): The list of channels for the main output.\n
        **buffer_options** (*dict*): Buffer options.\n
            **clear_output_buffer_on_data_input** (*bool*): Whether to clear the output buffer when new data is inserted in the input buffer.\n
            **clear_input_buffer_after_process** (*bool*): Whether to clear the input buffer after processing.\n
            **clear_output_buffer_after_process** (*bool*): Whether to clear the output buffer after


    Example:
    ```json
    {
        "module": "models.node.processing.metric.roc_auc",
        "type": "ROCAUC",
        "outputs": {
            "main": [
                {
                    "node": "console_output",
                    "input": "main"
                }
            ]
        },
        "buffer_options": {
            "clear_output_buffer_on_data_input": true,
            "clear_input_buffer_after_process": true,
            "clear_output_buffer_after_process": true
        }
    }
    ```

    In this example, the node calculates the ROC AUC score and outputs it to a console output node.

    """

    _MODULE_NAME: Final[str] = 'node.processing.metric.roc_auc'

    INPUT_PREDICTED: Final[str] = 'predicted'
    INPUT_ACTUAL: Final[str] = 'actual'
    OUTPUT_MAIN: Final[str] = 'main'

    def _validate_parameters(self, parameters: dict):
        """
        Validates the parameters passed to this node.
        :param parameters:
        :return:
        """
        super()._validate_parameters(parameters)

    def _initialize_parameter_fields(self, parameters: dict):
        """
        Initializes the parameter fields of this node.
        :param parameters:
        :return:
        """
        super()._initialize_parameter_fields(parameters)

    def _is_next_node_call_enabled(self) -> bool:
        """
        Checks whether the next node call is enabled.
        :return: True if the output buffer contains any data
        """
        return self._output_buffer[self.OUTPUT_MAIN].get_data_count() > 0

    def _is_processing_condition_satisfied(self) -> bool:
        """
        Checks if the processing condition is satisfied.
        :return: True if the input buffers contain data and the predicted and actual data have the same number of samples
        """
        return (self._input_buffer[self.INPUT_PREDICTED].get_data_count() > 0
                and self._input_buffer[self.INPUT_ACTUAL].get_data_count() > 0
                and self._input_buffer[self.INPUT_PREDICTED].get_data_count() == self._input_buffer[self.INPUT_ACTUAL].get_data_count()
                )

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        """
        Processes the data.
        Calculate the ROC AUC score.
        This method gets the data as 2D arrays, and transposes it using numpy. then, it calculates the ROC AUC score using the sklearn library.
        :param data: {"predicted": FrameworkData, "actual": FrameworkData}
        :return: Framework data containing a single entry with the ROC AUC score
        """
        predicted = np.transpose(data[self.INPUT_PREDICTED].get_data_as_2d_array())
        actual = np.transpose(data[self.INPUT_ACTUAL].get_data_as_2d_array())
        roc_auc = metrics.roc_auc_score(actual, predicted)
        output = FrameworkData(sampling_frequency_hz=1)
        output.input_data_on_channel([roc_auc])
        return {
            self.OUTPUT_MAIN: output
        }

    def _get_inputs(self) -> List[str]:
        """
        Returns the inputs of this node.
        :return: inputs of node as List[str]
        """
        return [
            self.INPUT_PREDICTED,
            self.INPUT_ACTUAL
        ]

    def _get_outputs(self) -> List[str]:
        """
        Returns the outputs of this node.
        :return: outputs of node as List[str]
        """
        return [
            self.OUTPUT_MAIN
        ]