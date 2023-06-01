import abc
from typing import Final, Any

import mne.decoding
import numpy as np
from sklearn.base import TransformerMixin, BaseEstimator

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.processing.trainable.feature_extractor.sklearn_feature_extractor import SKLearnFeatureExtractor


class CSP(SKLearnFeatureExtractor):
    """ This node is a wrapper for the sklearn CSP feature extractor. A CSP is used for M/EEG signal decomposition using 
    the Common Spatial Patterns (CSP). This node can be used as a supervised decomposition to estimate spatial 
    filters for feature extraction in a 2 class decoding problem.

    Attributes:
        _MODULE_NAME (str): The name of the module(in this case ``node.processing.trainable.feature_extractor.csp``)
    
    configuration.json usage:
        **module** (*str*): The name of the module (``node.processing.trainable.feature_extractor``)\n
        **type** (*str*): The type of the node (``CSP``)\n
        **number_of_components** (*int*): The number of components to decompose the signal into.\n
        **training_set_size** (*int*): The size of the training set in samples.\n
        **save_after_training** (*bool*): Whether to save the trained processor after training. This is a optional parameter.\n
        **save_file_path** (*str*): The path to save the trained processor if ``save_after_training`` is True. Only mandatory if ``save_after_training`` is True.\n
        **load_trained** (*bool*): Whether to load a trained processor.\n
        **load_file_path** (*str*): The path to load the trained processor if ``load_trained`` is True. Only mandatory if ``load_trained`` is True.\n
        **buffer_options** (*dict*): Buffer options.\n
            **clear_input_buffer_after_training** (*bool*): Whether to clear the input buffer after training.\n
            **process_input_buffer_after_training** (*bool*): Whether to process the input buffer after training.\n
            **clear_output_buffer_on_data_input** (*bool*): Whether to clear the output buffer when new data is inserted in the input buffer.\n
            **clear_input_buffer_after_process** (*bool*): Whether to clear the input buffer after processing.\n
            **clear_output_buffer_after_process** (*bool*): Whether to clear the output buffer after processing.\n

    """
    _MODULE_NAME: Final[str] = 'node.processing.trainable.feature_extractor.csp'

    @abc.abstractmethod
    def _validate_parameters(self, parameters: dict):
        """ Validates the parameters passed to this node. In this case it checks if the parameters are present and if they
        are of the correct type.

        :param parameters: The parameters passed to this node.
        :type parameters: dict

        :raises MissingParameterError: the ``number_of_components`` parameter is required.
        :raises InvalidParameterValue: the ``number_of_components`` parameter must be an int.
        """
        super()._validate_parameters(parameters)
        if 'number_of_components' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME,name=self.name,
                                        parameter='number_of_components')
        if type(parameters['number_of_components']) is not int:
            raise InvalidParameterValue(module=self._MODULE_NAME,name=self.name,
                                        parameter='number_of_components',
                                        cause='must_be_int')

    @abc.abstractmethod
    def _initialize_parameter_fields(self, parameters: dict):
        """ Initializes the parameter fields of this node. In this case it initializes the ``number_of_components``
        parameter and the parent node parameters as well.
        
        :param parameters: The parameters passed to this node.
        :type parameters: dict
        """
        self.number_of_components = parameters['number_of_components']
        super()._initialize_parameter_fields(parameters)

    def _initialize_trainable_processor(self) -> (TransformerMixin, BaseEstimator):
        """ Initializes the trainable processor of this node. In this case it initializes the sklearn CSP processor.

        :return: The initialized sklearn CSP processor.
        :rtype: (TransformerMixin, BaseEstimator)
        """
        return mne.decoding.CSP(n_components=self.number_of_components)

    @abc.abstractmethod
    def _should_retrain(self) -> bool:
        """ Returns whether the processor should be retrained. In this case it returns False always.

        :return: Whether the processor should be retrained.
        :rtype: bool
        """
        return False

    @abc.abstractmethod
    def _is_next_node_call_enabled(self) -> bool:
        """ Returns whether the next node call is enabled. In this case it returns True if the processor is trained and
        the output buffer has data.

        :return: Whether the next node call is enabled.
        :rtype: bool
        """
        return self._is_trained and self._output_buffer[self.OUTPUT_MAIN].has_data()

    def _format_processed_data(self, processed_data: Any, sampling_frequency: float) -> FrameworkData:
        """ Formats the processed data so that it can be passed to the next node. In this case it moves the channels axis
        to the first position and creates a FrameworkData object with the processed data.

        :param processed_data: The processed data.
        :type processed_data: Any
        :param sampling_frequency: The sampling frequency of the processed data.
        :type sampling_frequency: float

        :return: The formatted processed data.
        :rtype: FrameworkData
        """
        processed_data = np.moveaxis(processed_data, 1, 0)
        formatted_data = FrameworkData(sampling_frequency_hz=sampling_frequency,
                                       channels=[f'source_{i}' for i in range(1, self.number_of_components+1)])
        formatted_data.input_2d_data(processed_data)
        return formatted_data
