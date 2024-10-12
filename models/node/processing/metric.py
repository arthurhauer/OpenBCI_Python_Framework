from typing import Final, List, Any, Dict

import numpy
from sklearn.metrics import *

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode


class Metric(ProcessingNode):
    """ This node output user-selected metric from given ``FrameworkData`` in input 'actual', containing the actual true
    labels, and ``FrameworkData`` in input 'predicted', containing the predicted class outputted from a classifier node.
    The currently supported options for the 'metric' parameter are:
     - accuracy
    The following example depicts, a node named 'metric', in which the 'accuracy' metric is selected. In this
    example, the calculated accuracy is then outputted to a node named 'csv_output'.

    .. code-block::

        "metric": {
            "module": "models.node.processing",
            "type": "Metric",
            "metric": "accuracy",
            "buffer_options": {
                "clear_output_buffer_on_data_input": true,
                "clear_input_buffer_after_process": true,
                "clear_output_buffer_after_process": true
            },
            "outputs": {
                "main": [
                    {
                        "node": "csv_output",
                        "input": "main"
                    }
                ]
            }
        }

    Attributes:
        _MODULE_NAME (str): The name of the module(in this case ``node.processing.metric``)
        INPUT_ACTUAL (str): The name of the main input(in this case ``actual``)
        INPUT_PREDICTED (str): The name of the main input(in this case ``predicted``)
        OUTPUT_MAIN (str): The name of the main output(in this case ``main``)

    ``configuration.json`` usage:
        **module** (*str*): Current module name (in this case ``models.node.processing``).\n
        **type** (*str*): Current node type (in this case ``Merge``).\n
        **metric** (*str*): Selected metric.
        **buffer_options** (*dict*): Buffer options:
            **clear_output_buffer_on_data_input** (*bool*): If ``True``, the output buffer will be cleared when data is inputted.\n
            **clear_input_buffer_after_process** (*bool*): If ``True``, the input buffer will be cleared after the node is executed.\n
            **clear_output_buffer_after_process** (*bool*): If ``True``, the output buffer will be cleared after the node is executed.\n
    """
    _MODULE_NAME: Final[str] = 'node.processing.metric'

    INPUT_ACTUAL: Final[str] = 'actual'
    INPUT_PREDICTED: Final[str] = 'predicted'
    OUTPUT_MAIN: Final[str] = 'main'

    _SUPPORTED_METRICS: Final[List[str]] = [
        'accuracy'
    ]

    def _validate_parameters(self, parameters: dict):
        """Validates the parameters that were passed to the node. In this case it calls the parent method and validates the 'dictionary' parameter format.
        """
        super()._validate_parameters(parameters)
        if 'metric' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='metric')
        if type(parameters['metric']) is not str:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='metric',
                                        cause='must_be_str')
        if parameters['metric'] not in self._SUPPORTED_METRICS:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='metric',
                                        cause='must_be_one_of_SUPPORTED_METRICS')

    def _initialize_parameter_fields(self, parameters: dict):
        """Initializes the parameters that were passed to the node. In this case it calls the parent method and initializes the renaming dictionary for data processing.
        """
        super()._initialize_parameter_fields(parameters)
        self._metric_function = self._select_metric(parameters['metric'])

    def _select_metric(self, metric: str) -> Any:
        if metric == 'accuracy':
            return accuracy_score
        raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                    parameter='metric',
                                    cause='must_be_one_of_SUPPORTED_METRICS')

    def _is_next_node_call_enabled(self) -> bool:
        """ This method allows the next node call. In this case it enables whenever there's data in the output buffer.
        """
        return self._output_buffer[self.OUTPUT_MAIN].get_data_count() > 0

    def _is_processing_condition_satisfied(self) -> bool:
        """ This method will return ``True`` if the processing condition is satisfied. This method will return ``True``
        if the input buffer has data.

        :return: ``True`` if the input buffer has data, ``False`` otherwise.
        :rtype: bool
        """
        return self._input_buffer[self.INPUT_ACTUAL].get_data_count() > 0 \
               and self._input_buffer[self.INPUT_ACTUAL].get_data_count() >= self._input_buffer[
                   self.INPUT_PREDICTED].get_data_count() \
               and self._input_buffer[self.INPUT_PREDICTED].get_data_count() > 0

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        """ This method processes the data that was inputted to the node. It calculates classification performance
         using user-selected metric.

        :param data: The data that was inputted to the node.
        :type data: Dict[str, FrameworkData]

        :return: The calculated performance metric.
        :rtype: Dict[str, FrameworkData]
        """
        predicted_labels = numpy.array(data[self.INPUT_PREDICTED].get_data_single_channel()).repeat(150)
        actual_labels = data[self.INPUT_ACTUAL].get_data_single_channel()[0:len(predicted_labels)]
        unformatted_metric = self._metric_function(actual_labels, predicted_labels)

        calculated_metric = FrameworkData()
        calculated_metric.input_data_on_channel([unformatted_metric])

        return {
            self.OUTPUT_MAIN: calculated_metric
        }

    def _clear_input_buffer(self):
        if not hasattr(self, '_input_buffer'):
            super()._clear_input_buffer()
            return
        self._input_buffer[self.INPUT_ACTUAL].splice(0, self._input_buffer[self.INPUT_PREDICTED].get_data_count())
        self._input_buffer[self.INPUT_PREDICTED] = FrameworkData()

    def _get_inputs(self) -> List[str]:
        """ This method returns the inputs of the node. In this case it returns a single 'main' input.
        """
        return [
            self.INPUT_ACTUAL,
            self.INPUT_PREDICTED
        ]

    def _get_outputs(self) -> List[str]:
        """ This method returns the outputs of the node. In this case it returns a single 'main' output.
        """
        return [
            self.OUTPUT_MAIN
        ]
