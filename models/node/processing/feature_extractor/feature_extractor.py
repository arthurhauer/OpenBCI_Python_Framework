import abc
from typing import List, Dict, Final
from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode


class FeatureExtractor(ProcessingNode):
    """ This is the base class for all feature extractors. A feature extractor is a node that extracts features from a dataset.

    Attributes:
        _MODULE_NAME (`str`): The name of the module (in his case ``node.processing.feature_extractor.feature_extractor``)

    configuration.json usage:
        **module** (*str*): The name of the module (``node.processing.feature_extractor``)\n
        **type** (*str*): The type of the node (``FeatureExtractor``)\n
        **buffer_options** (*dict*): Buffer options.\n
            **clear_output_buffer_on_data_input** (*bool*): Whether to clear the output buffer when new data is inserted in the input buffer.\n
            **clear_input_buffer_after_process** (*bool*): Whether to clear the input buffer after processing.\n
            **clear_output_buffer_after_process** (*bool*): Whether to clear the output buffer after processing.\n 
    """

    _MODULE_NAME: Final[str] = 'node.processing.feature_extractor.feature_extractor'

    def __init__(self, parameters: dict):
        super().__init__(parameters)
        self._validate_parameters(parameters)

    @abc.abstractmethod
    def _validate_parameters(self, parameters: dict):
        """ Validates the parameters passed to this node. In this case it just calls the super method from ProcessingNode.

        :param parameters: The parameters passed to this node.
        :type parameters: dict
        """
        super()._validate_parameters(parameters)

    @abc.abstractmethod
    def _initialize_parameter_fields(self, parameters: dict):
        """ Initializes the parameter fields of this node. In this case it just calls the super method from ProcessingNode.

        :param parameters: The parameters passed to this node.
        :type parameters: dict
        """
        super()._initialize_parameter_fields(parameters)

    @classmethod
    def from_config_json(cls, parameters: dict):
        """ Adds the configuration.json parameters to a new instance of this class.
        
        :param parameters: The parameters passed to this node.
        :type parameters: dict
        """
        return cls(parameters)

    def _is_next_node_call_enabled(self) -> bool:
        """ Returns whether the next node call is enabled. It's always enabled for this node.
        """
        return True

    def _is_processing_condition_satisfied(self) -> bool:
        """ Returns whether the processing condition is satisfied. The processing condition is satisfied if the input buffer is not empty.
        """
        return self._input_buffer[self.INPUT_MAIN].get_data_count() > 0

    @abc.abstractmethod
    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        """ This method extracts features from the data. It should be implemented by the subclasses.

        :param data: The data to process.
        :type data: dict[str, FrameworkData]

        :raises NotImplementedError: This method should be implemented by the subclasses.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def _get_inputs(self) -> List[str]:
        """ Returns the inputs of this node. It should be implemented by the subclasses.

        :raises NotImplementedError: This method should be implemented by the subclasses.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def _get_outputs(self) -> List[str]:
        """ Returns the outputs of this node. It should be implemented by the subclasses.

        :raises NotImplementedError: This method should be implemented by the subclasses.
        """
        raise NotImplementedError()
