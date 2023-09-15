import abc
from typing import Final, Any

from sklearn.base import TransformerMixin, BaseEstimator
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.processing.trainable.classifier.sklearn_classifier import SKLearnClassifier


class LDA(SKLearnClassifier):
    """ This node is a wrapper for the ``LinearDiscriminantAnalysis`` classifier from sklearn. It is a subclass of
    ``SKLearnClassifier`` and implements the abstract methods from it. The ``LinearDiscriminantAnalysis`` classifier
    can be used to classify data into two or more classes. 

    Attributes:
        _MODULE_NAME (str): The name of the module(in this case ``node.processing.trainable.classifier.lda``)

    configuration.json usage: 
        **module** (*str*): The name of the module (``node.processing.trainable.classifier``)\n
        **type** (*str*): The name of the class (``LDA``)\n
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
    _MODULE_NAME: Final[str] = 'node.processing.trainable.classifier.lda'

    @abc.abstractmethod
    def _validate_parameters(self, parameters: dict):
        """ Validates the parameters passed to this node. In this case it checks if the parameters are present and if they
        are of the correct type, extending the from its superclass.

        :param parameters: The parameters to validate.
        :type parameters: dict
        """
        super()._validate_parameters(parameters)

    def _initialize_parameter_fields(self, parameters: dict):
        """ Initializes the parameters of this node. In this case it initializes the parameters from its superclass and
        adds the parameters specific to this node.

        :param parameters: The parameters to initialize.
        :type parameters: dict
        """
        super()._initialize_parameter_fields(parameters)

    def _initialize_trainable_processor(self) -> (TransformerMixin, BaseEstimator):
        """ Initializes the trainable processor. In this case it initializes the ``LinearDiscriminantAnalysis`` classifier
        from sklearn.

        :return: The initialized ``LinearDiscriminantAnalysis`` classifier.
        :rtype: (TransformerMixin, BaseEstimator)
        """
        return LinearDiscriminantAnalysis()

    @abc.abstractmethod
    def _should_retrain(self) -> bool:
        """ Checks if the processor should be retrained. In this case it always returns False, so the processor will
        never be retrained.
        """
        return False

    @abc.abstractmethod
    def _is_next_node_call_enabled(self) -> bool:
        """ Checks if the next node call is enabled. In this case it checks if the processor is trained and if the
        output buffer has data.
        """
        return self._is_trained and self._output_buffer[self.OUTPUT_MAIN].has_data()

    def _format_processed_data(self, processed_data: Any, sampling_frequency: float) -> FrameworkData:
        """ Formats the processed data. In this case it creates a ``FrameworkData`` object and adds the processed data
        to it. 

        :param processed_data: The processed data.
        :type processed_data: Any
        :param sampling_frequency: The sampling frequency of the processed data.
        :type sampling_frequency: float

        :return: The formatted data.
        :rtype: FrameworkData
        """
        formatted_data = FrameworkData(sampling_frequency_hz=sampling_frequency)
        formatted_data.input_data_on_channel(processed_data)
        return formatted_data
