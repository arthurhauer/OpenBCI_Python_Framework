import abc
from typing import List, Dict, Final
from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode


class Segmenter(ProcessingNode):
    """ This is the base class for all segmenters. A segmenter is a node that segments the input data into smaller parts.
    In many applications of the signal processing such as automatic analysis of EEG signal, it is needed that signal is 
    split to smaller parts that each part has the same statistical characterizations such as the amplitude and frequency.
    This is called segmentation. This class does that by segmenting the input data into smaller parts. The segmentation
    itself is done by the segment_data method that must be implemented by the subclasses.

    Attributes:
        _MODULE_NAME (`str`): The name of the module (in his case ``node.processing.segmenter.segmenter``)
        INPUT_MAIN (`str`): The name of the main input (``main``)
        OUTPUT_MAIN (`str`): The name of the main output (``main``)
    """
    _MODULE_NAME: Final[str] = 'node.processing.segmenter.segmenter'

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

    def _is_next_node_call_enabled(self) -> bool:
        """ Returns whether the next node call is enabled. It's always enabled for this node.
        """
        return True

    def _is_processing_condition_satisfied(self) -> bool:
        """ Returns whether the processing condition is satisfied. In this case it returns True if there is data in the
        input buffer.
        """
        return self._input_buffer[self.INPUT_MAIN].get_data_count() > 0

    @abc.abstractmethod
    def segment_data(self, data: FrameworkData) -> FrameworkData:
        """ This method segments the data. It must be implemented by the subclasses.
        """
        raise NotImplementedError()

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        """ This method segments the data. It calls the segment_data method for each data in the FrameworkData object.
        """
        segmented_data: Dict[str, FrameworkData] = {}
        for key in data:
            segmented_data[key] = self.segment_data(data[key])
        return segmented_data

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
