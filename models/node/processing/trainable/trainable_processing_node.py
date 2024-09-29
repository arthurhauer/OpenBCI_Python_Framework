import abc
import os
from typing import Final, List, Any

import joblib

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode


class TrainableProcessingNode(ProcessingNode):
    """ This node is base node for trainable nodes. It implements a generic training logic that can be used by all
    trainable nodes. This node must be extended by all trainable nodes so that the correct parameters are passed to the
    extended class and the correct methods are implemented.

    Attributes:
        _MODULE_NAME (`str`): The name of the module (in his case ``node.processing.trainable``)
        INPUT_DATA (`str`): The name of the input data (in his case ``data``)
        INPUT_LABEL (`str`): The name of the input label (in his case ``label``)
    
    This node should not be used directly in the configuration.json file. Instead, it should be extended by other nodes
    that implement the training logic. But every node that extends this node will have the following parameters in the
    configuration.json file:
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
    _MODULE_NAME: Final[str] = 'models.node.processing.trainable'

    INPUT_DATA: Final[str] = 'data'
    INPUT_LABEL: Final[str] = 'label'

    @abc.abstractmethod
    def _validate_parameters(self, parameters: dict):
        """ Validates the parameters passed to this node. In this case it checks if the parameters are present and if they
        are of the correct type.

        :param parameters: The parameters passed to this node.
        :type parameters: dict

        :raises MissingParameterError: the ``training_set_size`` parameter is required.
        :raises InvalidParameterValue: the ``training_set_size`` parameter must be an int.
        :raises InvalidParameterValue: the ``training_set_size`` parameter must be greater than 0.
        :raises MissingParameterError: the ``save_after_training`` parameter is required.
        :raises InvalidParameterValue: the ``save_after_training`` parameter must be a bool.
        :raises MissingParameterError: the ``save_file_path`` parameter is required.
        :raises InvalidParameterValue: the ``save_file_path`` parameter must be a str.
        :raises MissingParameterError: the ``load_trained`` parameter is required.
        :raises InvalidParameterValue: the ``load_trained`` parameter must be a bool.
        :raises MissingParameterError: the ``load_file_path`` parameter is required.
        :raises InvalidParameterValue: the ``load_file_path`` parameter must be a str.
        :raises InvalidParameterValue: the ``load_file_path`` parameter must be a valid path.
        :raises MissingParameterError: the ``clear_input_buffer_after_training`` parameter is required.
        :raises InvalidParameterValue: the ``clear_input_buffer_after_training`` parameter must be a bool.
        :raises MissingParameterError: the ``process_input_buffer_after_training`` parameter is required.
        :raises InvalidParameterValue: the ``process_input_buffer_after_training`` parameter must be a bool.

        
        """
        super()._validate_parameters(parameters)
        if 'training_set_size' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='training_set_size')
        if 'clear_input_buffer_after_training' not in parameters['buffer_options']:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='buffer_options.clear_input_buffer_after_training')
        if type(parameters['training_set_size']) is not int:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='training_set_size',
                                        cause='must_be_int')
        if parameters['training_set_size'] < 1:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='training_set_size',
                                        cause='must_be_greater_than_0')
        if type(parameters['buffer_options']['clear_input_buffer_after_training']) is not bool:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='buffer_options.clear_input_buffer_after_training',
                                        cause='must_be_bool')
        if parameters['buffer_options']['clear_input_buffer_after_training'] is False:
            if 'process_input_buffer_after_training' not in parameters['buffer_options']:
                raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                            parameter='buffer_options.process_input_buffer_after_training')
            if type(parameters['buffer_options']['process_input_buffer_after_training']) is not bool:
                raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                            parameter='buffer_options.process_input_buffer_after_training',
                                            cause='must_be_bool')
        if 'save_after_training' not in parameters:
            parameters['save_after_training'] = False

        if type(parameters['save_after_training']) is not bool:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='save_after_training',
                                        cause='must_be_bool')
        if parameters['save_after_training'] is True:
            if 'save_file_path' not in parameters:
                raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                            parameter='save_file_path')
            # TODO validate path str
            if type(parameters['save_file_path']) is not str:
                raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                            parameter='save_file_path',
                                            cause='must_be_str')
        if 'load_trained' not in parameters:
            parameters['load_trained'] = False

        if type(parameters['load_trained']) is not bool:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='load_trained',
                                        cause='must_be_bool')
        if parameters['load_trained'] is True:
            if 'load_file_path' not in parameters:
                raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                            parameter='load_file_path')
            if type(parameters['load_file_path']) is not str:
                raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                            parameter='load_file_path',
                                            cause='must_be_str')
            if not os.path.exists(parameters['load_file_path']):
                raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                            parameter='load_file_path',
                                            cause='file_doesnt_exist')

    @abc.abstractmethod
    def _initialize_parameter_fields(self, parameters: dict):
        """ TrainableProcessingNode node implementation of buffer behaviour options initialization and custom parameter
        fields initialization.

        :param parameters: The parameters passed to this node.
        :type parameters: dict
        """
        super()._initialize_parameter_fields(parameters)
        self._clear_input_buffer_after_training: bool = parameters['buffer_options'][
            'clear_input_buffer_after_training']
        self._process_input_buffer_after_training: bool = False \
            if parameters['buffer_options']['clear_input_buffer_after_training'] \
            else parameters['buffer_options']['process_input_buffer_after_training']
        self.training_set_size: int = parameters['training_set_size']

        self._is_trained: bool = False

        if parameters['load_trained']:
            self.print(f'Loading trained processor from {parameters["load_file_path"]}')
            self._is_trained: bool = True
            trained_processor = joblib.load(parameters['load_file_path'])
            self._load_trained_processor(trained_processor)

        self._save_after_training = parameters['save_after_training']
        if self._save_after_training:
            self._save_file_path = parameters['save_file_path']

    @abc.abstractmethod
    def _load_trained_processor(self, loaded_processor: Any) -> None:
        """ Loads a trained processor. This method must be implemented by the subclasses.

        :param loaded_processor: The loaded processor.
        :type loaded_processor: Any

        :raises NotImplementedError: This method must be implemented by the subclasses.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def _save_trained_processor(self, save_path: str) -> None:
        """ Saves a trained processor. This method must be implemented by the subclasses.

        :param save_path: The path to save the trained processor.
        :type save_path: str

        :raises NotImplementedError: This method must be implemented by the subclasses.
        """
        raise NotImplementedError()

    def _process_input_buffer(self):
        """ TrainableProcessingNode node implementation of the processing logic. This method is called when the
        processing condition is satisfied. In this case, the processing condition is satisfied when the input buffer
        has at least ``training_set_size`` samples. This method will call the ``_train`` method to train the processor
        and then it will save the trained processor if ``save_after_training`` is True and clear the input buffer if
        ``clear_input_buffer_after_training`` is True. If ``clear_input_buffer_after_training`` is False, it will
        process the input buffer if ``process_input_buffer_after_training`` is True.
        The self._train method must be implemented by the subclasses. But normally it is a library method that trains
        the processor. For example, in the case of the sklearn compatible nodes, the ``_train`` method is the
        ``fit`` method of the sklearn processor.
        """
        if self._is_trained:
            super()._process_input_buffer()
            if self._should_retrain():
                self._is_trained = False
            else:
                return
        if not self._is_training_condition_satisfied():
            return
        self.print(f'Starting training of {self._MODULE_NAME}')
        self._train(self._input_buffer[self.INPUT_DATA], self._input_buffer[self.INPUT_LABEL])
        self.print(f'Finished training of {self._MODULE_NAME}')
        self._is_trained = True
        if self._save_after_training:
            self.print(f'Saving trained {self._MODULE_NAME}')
            save_path = self._save_file_path

            if not os.path.exists('\\'.join(save_path.split('\\')[0:-1])):
                os.makedirs('\\'.join(save_path.split('\\')[0:-1]))
            self._save_trained_processor(save_path)

        if self._clear_input_buffer_after_training:
            super()._clear_input_buffer()
            return
        if self._process_input_buffer_after_training:
            self.print(f'Processing data on {self._MODULE_NAME}')
            super()._process_input_buffer()
            return

    @abc.abstractmethod
    def _train(self, data: FrameworkData, label: FrameworkData):
        """ Trains the processor. This method must be implemented by the subclasses.

        :param data: The data to train the processor.
        :type data: FrameworkData
        :param label: The label to train the processor.
        :type label: FrameworkData

        :raises NotImplementedError: This method must be implemented by the subclasses.
        """
        raise NotImplementedError()

    def _is_training_condition_satisfied(self) -> bool:
        """ Returns whether the training condition is satisfied. In this case it returns True if the input buffer has
        at least ``training_set_size`` samples.

        :return: Whether the training condition is satisfied.
        :rtype: bool
        """
        return self._input_buffer[self.INPUT_DATA].get_data_count() >= self.training_set_size \
               and self._input_buffer[self.INPUT_LABEL].get_data_count() >= self.training_set_size

    def _is_processing_condition_satisfied(self) -> bool:
        """ Returns whether the processing condition is satisfied. In this case it returns True if the input buffer
        has at least one sample.

        :return: Whether the processing condition is satisfied.
        :rtype: bool
        """
        return self._input_buffer[self.INPUT_DATA].get_data_count() > 0

    @abc.abstractmethod
    def _should_retrain(self) -> bool:
        """ Returns whether the processor should be retrained. This method must be implemented by the subclasses.

        :raises NotImplementedError: This method must be implemented by the subclasses.
        """

        raise NotImplementedError()

    def _get_inputs(self) -> List[str]:
        """ Returns the inputs of this node. In this case it returns the ``INPUT_DATA`` and ``INPUT_LABEL``.

        :return: The inputs of this node.
        :rtype: List[str]
        """
        return [
            self.INPUT_DATA,
            self.INPUT_LABEL
        ]
