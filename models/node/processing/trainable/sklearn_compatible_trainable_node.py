import abc
from typing import List, Dict, Final, Any
from statistics import mode

import joblib
import numpy as np
from sklearn.base import TransformerMixin, BaseEstimator

from models.framework_data import FrameworkData
from models.node.processing.trainable.trainable_processing_node import TrainableProcessingNode


class SKLearnCompatibleTrainableNode(TrainableProcessingNode):
    """ Base class for all trainable processing nodes that use sklearn processors. SKLear has multiple processors
    that can be used for different purposes. This class is used to wrap them and make them compatible with the
    framework. Many SKLearn processors return a ``TransformerMixin`` object, which is a transformer that can be used
    to transform data, and a ``BaseEstimator`` object, which is an estimator that can be used to train the transformer.
    This class is abstract and should be inherited by all nodes that use sklearn processors. 

    Attributes:
        _MODULE_NAME  (`str`): The name of the module (in his case ``node.processing.trainable.sklearn_compatible_trainable_node``)
        OUTPUT_MAIN (`str`): The name of the main output of the node (in this case ``main``)
    
    This node should not be used directly in the configuration.json file. But every node that extends this node will have the 
    following parameters in the configuration.json file:
        **module** (*str*): The name of the module (``node.processing``)\n
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
    _MODULE_NAME: Final[str] = 'node.processing.trainable.sklearn_compatible_trainable_node'

    OUTPUT_MAIN: Final[str] = 'main'

    @abc.abstractmethod
    def _validate_parameters(self, parameters: dict):
        """ Validates the parameters of the node. This method calls the parent method to validate the parameters of this node.

        :param parameters: The parameters of the node.
        :type parameters: dict
        """
        super()._validate_parameters(parameters)

    @abc.abstractmethod
    def _initialize_parameter_fields(self, parameters: dict):
        """ Initializes the parameter fields calling the parent method and initializes the ``sklearn_processor``.

        :param parameters: The parameters of the node.
        :type parameters: dict
        """
        self.sklearn_processor = None
        super()._initialize_parameter_fields(parameters)
        if self.sklearn_processor is None:
            self.sklearn_processor: (TransformerMixin, BaseEstimator) = self._initialize_trainable_processor()

    @abc.abstractmethod
    def _initialize_trainable_processor(self) -> (TransformerMixin, BaseEstimator):
        """ Initializes the trainable processor. This method should be implemented by the subclasses.

        :raises NotImplementedError: If the method is not implemented by the subclass.
        """
        raise NotImplementedError()

    def _load_trained_processor(self, loaded_processor: Any) -> None:
        """ Loads a trained processor in the node initialization.
        """
        self.sklearn_processor = loaded_processor

    @abc.abstractmethod
    def _save_trained_processor(self, save_path: str) -> None:
        """ Saves the trained data in the file specified in the ``save_file_path`` parameter if ``save_after_training`` is True.
        This is done joblib.dump that persist an arbitrary Python object into one file, in this case the sklearn processor.
        """
        joblib.dump(self.sklearn_processor, save_path)

    @classmethod
    def from_config_json(cls, parameters: dict):
        """ Creates a new instance of this node using the parameters specified in the configuration.json file.

        :param parameters: The parameters of the node.
        :type parameters: dict

        :return: A new instance of this node.
        :rtype: SKLearnCompatibleTrainableNode
        """
        return cls(parameters)

    @abc.abstractmethod
    def _should_retrain(self) -> bool:
        """ Returns whether the node should retrain the processor. This method should be implemented by the subclasses.

        :raises NotImplementedError: If the method is not implemented by the subclass.
        """
        raise NotImplementedError()

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        """ This method formats the raw data and then processes it. This is just a generic pipeline that should be used by all
        nodes that extend this node. The developer must implement the ``_inner_process_data`` and ``_format_processed_data`` methods,
        so that the data is processed and formatted according to the node needs.

        :param data: The data to process.
        :type data: dict(str, FrameworkData)

        :return: The processed data.
        :rtype: defined by the developer in the ``_format_processed_data`` method.
        """
        raw_data: Any = self._format_raw_data(data[self.INPUT_DATA])
        processed_data: Any = self._inner_process_data(raw_data)
        return {
            self.OUTPUT_MAIN: self._format_processed_data(processed_data, data[self.INPUT_DATA].sampling_frequency)
        }

    def _format_raw_data(self, raw_data: FrameworkData) -> Any:
        """ Formats the raw data. This method is used to format the raw data in a way that is compatible with the sklearn processors.
        It first converts the raw data to a numpy 2d array and then moves the axis to the first position.

        :param raw_data: The raw data to format.
        :type raw_data: FrameworkData

        :return: The formatted data.
        :rtype: ndarray
        """
        formatted_data = np.asarray(raw_data.get_data_as_2d_array())
        formatted_data = np.moveaxis(formatted_data, 1, 0)
        # if len(formatted_data.shape) > 2:
        #     formatted_data = formatted_data.reshape(formatted_data.shape[0], formatted_data.shape[1]*formatted_data.shape[2])
        return formatted_data

    def _format_raw_label(self, raw_label: FrameworkData) -> Any:
        """ This method add to each raw data epoch the according label. This is done by getting the most common value of each epoch
        and adding it to the label list. Then the label list is converted to a numpy array and stored in the class variable
        ``_format_raw_label``.

        :param raw_label: The raw label to format.
        :type raw_label: FrameworkData

        :return: The formatted label.
        :rtype: ndarray
        """
        formatted_label = []
        for epoch in raw_label.get_data_single_channel():
            formatted_epoch = epoch
            if(len(epoch)>1):
                formatted_epoch = mode(epoch)
            formatted_label.append(formatted_epoch)
        formatted_label = np.asarray(formatted_label)
        return formatted_label

    @abc.abstractmethod
    def _format_processed_data(self, processed_data: Any, sampling_frequency: float) -> FrameworkData:
        """ Formats the processed data. This method is used to format the processed data in a way that is compatible with the framework.
        This method should be implemented by the subclasses.

        :param processed_data: The processed data to format.
        :type processed_data: Any
        :param sampling_frequency: The sampling frequency of the processed data.
        :type sampling_frequency: float

        :raises NotImplementedError: If the method is not implemented by the subclass.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def _inner_process_data(self, data: Any) -> Any:
        """ Processes the data. This method is used to process the data using the sklearn processor. This method should be implemented
        by the subclasses.

        :param data: The data to process.
        :type data: Any

        :raises NotImplementedError: If the method is not implemented by the subclass.
        """
        raise NotImplementedError()

    def _inner_train_processor(self, data: Any, label: Any):
        """ The SKLearn processor is trained using the ``fit`` method. This method is used to train the processor using the data and
        label passed as parameters. This method just calls the ``fit`` method of the sklearn processor, that can be any sklearn processor.

        :param data: The data to train the processor.
        :type data: Any
        :param label: The label to train the processor.
        :type label: Any

        :return: The trained processor.
        :rtype: Any
        """
        return self.sklearn_processor.fit(data, label)

    def _train(self, data: FrameworkData, label: FrameworkData):
        """ This method is used to train the processor. This is method just get the raw data and label, formats them 
        and then calls the ``_inner_train_processor`` method that will train the processor. This is done for each set 
        size specified in the ``training_set_size`` parameter.
        """
        formatted_data = self._format_raw_data(data)
        formatted_label = self._format_raw_label(label)
        self._inner_train_processor(formatted_data[0:self.training_set_size], formatted_label[0:self.training_set_size])

    @abc.abstractmethod
    def _is_next_node_call_enabled(self) -> bool:
        """ Returns whether the next node call is enabled"""
        return super()._is_next_node_call_enabled()

    @abc.abstractmethod
    def _get_outputs(self) -> List[str]:
        """ Returns the outputs of the node
        
        :return: The outputs of the node.
        :rtype: List[str]
        """
        return [
            self.OUTPUT_MAIN
        ]
