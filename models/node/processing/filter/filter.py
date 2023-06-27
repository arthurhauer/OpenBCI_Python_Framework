import abc
from typing import List, Dict, Final, Tuple
from scipy.signal import lfilter
from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode


class Filter(ProcessingNode):
    """ This is the base class for all filters. A filter is a node that filters the input data with a filter.
    It can be a lowpass, highpass, bandpass or bandstop filter for example.

    Attributes:
        _MODULE_NAME (`str`): The name of the module (in his case ``node.processing.filter.filter``)
        INPUT_MAIN (`str`): The name of the main input (``main``)
        OUTPUT_MAIN (`str`): The name of the main output (``main``)
    """
    _MODULE_NAME: Final[str] = 'node.processing.filter.filter'

    INPUT_MAIN: Final[str] = 'main'
    OUTPUT_MAIN: Final[str] = 'main'

    @abc.abstractmethod
    def _validate_parameters(self, parameters: dict):
        """ Validates the parameters passed to this node. In this case it just calls the super method from ProcessingNode.
        """
        super()._validate_parameters(parameters)

    @abc.abstractmethod
    def _initialize_parameter_fields(self, parameters: dict):
        """ Initializes the parameter fields of this node. In this case it just calls the super method from ProcessingNode.
        """
        super()._initialize_parameter_fields(parameters)

    def _set_filter(self, sampling_frequency_hz: float) -> None:
        """ Sets the filter coefficients. This method takes for granted that the _get_filter_coefficients method will
        return a tuple with two lists, the first one being the numerator and the second one the denominator. This is 
        usually a result of the scipy.signal.butter or similar method.
        """
        self._filter_numerator, self._filter_denominator = self._get_filter_coefficients(self.parameters,
                                                                                         sampling_frequency_hz)

    @abc.abstractmethod
    def _get_filter_coefficients(self, parameters: dict, sampling_frequency_hz: float) -> Tuple[list, list]:
        """ Returns the filter coefficients. This method must be implemented by the subclasses.

        :raises NotImplementedError: This method must be implemented by the subclasses.
        """
        raise NotImplementedError()

    def _is_next_node_call_enabled(self) -> bool:
        """ Returns whether the next node call is enabled. It's always enabled for this node.
        """
        return True

    def _is_processing_condition_satisfied(self) -> bool:
        """ Returns whether the processing condition is satisfied. In this case it returns True if there is data in the
        input buffer.
        """
        return self._input_buffer[self.INPUT_MAIN].get_data_count() > 0

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        """ This method filters the data. It applies the filter to the data in the input buffer and returns the filtered
        data in the output buffer.
        The signal is filtered using the scipy.signal.lfilter method.

        :param data: The data to be filtered.
        :type data: Dict[str, FrameworkData]

        :return: The filtered data.
        :rtype: Dict[str, FrameworkData]
        """
        filtered_data: Dict[str, FrameworkData] = {}
        for key in data:
            filtered_data[key] = FrameworkData(sampling_frequency_hz=data[key].sampling_frequency)
            b, a = self._get_filter_coefficients(self.parameters, data[key].sampling_frequency)
            for channel in data[key].channels:
                raw_signal = data[key].get_data_on_channel(channel)
                filtered_signal = lfilter(b, a, raw_signal)
                filtered_data[key].input_data_on_channel(filtered_signal, channel)

        return filtered_data

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
