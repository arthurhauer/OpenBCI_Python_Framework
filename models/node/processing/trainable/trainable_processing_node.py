import abc
import os
from typing import Final, List, final, Any

import joblib
import time

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode


class TrainableProcessingNode(ProcessingNode):
    _MODULE_NAME: Final[str] = 'models.node.processing.trainable'

    INPUT_DATA: Final[str] = 'data'
    INPUT_LABEL: Final[str] = 'label'

    @abc.abstractmethod
    def _validate_parameters(self, parameters: dict):
        super()._validate_parameters(parameters)
        if 'training_set_size' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME,
                                        parameter='training_set_size')
        if 'clear_input_buffer_after_training' not in parameters['buffer_options']:
            raise MissingParameterError(module=self._MODULE_NAME,
                                        parameter='buffer_options.clear_input_buffer_after_training')
        if type(parameters['training_set_size']) is not int:
            raise InvalidParameterValue(module=self._MODULE_NAME,
                                        parameter='training_set_size',
                                        cause='must_be_int')
        if parameters['training_set_size'] < 1:
            raise InvalidParameterValue(module=self._MODULE_NAME,
                                        parameter='training_set_size',
                                        cause='must_be_greater_than_0')
        if type(parameters['buffer_options']['clear_input_buffer_after_training']) is not bool:
            raise InvalidParameterValue(module=self._MODULE_NAME,
                                        parameter='buffer_options.clear_input_buffer_after_training',
                                        cause='must_be_bool')
        if parameters['buffer_options']['clear_input_buffer_after_training'] is False:
            if 'process_input_buffer_after_training' not in parameters['buffer_options']:
                raise MissingParameterError(module=self._MODULE_NAME,
                                            parameter='buffer_options.process_input_buffer_after_training')
            if type(parameters['buffer_options']['process_input_buffer_after_training']) is not bool:
                raise InvalidParameterValue(module=self._MODULE_NAME,
                                            parameter='buffer_options.process_input_buffer_after_training',
                                            cause='must_be_bool')
        if 'save_after_training' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME,
                                        parameter='save_after_training')
        if type(parameters['save_after_training']) is not bool:
            raise InvalidParameterValue(module=self._MODULE_NAME,
                                        parameter='save_after_training',
                                        cause='must_be_bool')
        if parameters['save_after_training'] is True:
            if 'save_file_path' not in parameters:
                raise MissingParameterError(module=self._MODULE_NAME,
                                            parameter='save_file_path')
            # TODO validate path str
            if type(parameters['save_file_path']) is not str:
                raise InvalidParameterValue(module=self._MODULE_NAME,
                                            parameter='save_file_path',
                                            cause='must_be_str')
        if 'load_trained' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME,
                                        parameter='load_trained')
        if type(parameters['load_trained']) is not bool:
            raise InvalidParameterValue(module=self._MODULE_NAME,
                                        parameter='load_trained',
                                        cause='must_be_bool')
        if parameters['load_trained'] is True:
            if 'load_file_path' not in parameters:
                raise MissingParameterError(module=self._MODULE_NAME,
                                            parameter='load_file_path')
            if type(parameters['load_file_path']) is not str:
                raise InvalidParameterValue(module=self._MODULE_NAME,
                                            parameter='load_file_path',
                                            cause='must_be_str')
            if not os.path.exists(parameters['load_file_path']):
                raise InvalidParameterValue(module=self._MODULE_NAME,
                                            parameter='load_file_path',
                                            cause='file_doesnt_exist')

    @abc.abstractmethod
    def _initialize_parameter_fields(self, parameters: dict):
        super()._initialize_parameter_fields(parameters)
        self._clear_input_buffer_after_training: bool = parameters['buffer_options'][
            'clear_input_buffer_after_training']
        self._process_input_buffer_after_training: bool = False \
            if parameters['buffer_options']['clear_input_buffer_after_training'] \
            else parameters['buffer_options']['process_input_buffer_after_training']
        self.training_set_size: int = parameters['training_set_size']

        self._is_trained: bool = False

        if parameters['load_trained']:
            self._is_trained: bool = True
            self._load_trained_processor(joblib.load(parameters['load_file_path']))

        self._save_after_training = parameters['save_after_training']
        if self._save_after_training:
            self._save_file_path = parameters['save_file_path']

    @abc.abstractmethod
    def _load_trained_processor(self, loaded_processor: Any) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def _save_trained_processor(self, save_path: str) -> None:
        raise NotImplementedError()

    def _process_input_buffer(self):
        if self._is_trained:
            super()._process_input_buffer()
            if self._should_retrain():
                self._is_trained = False
            else:
                return
        if not self._is_training_condition_satisfied():
            return

        self._train(self._input_buffer[self.INPUT_DATA], self._input_buffer[self.INPUT_LABEL])
        self._is_trained = True
        if self._save_after_training:
            self._save_trained_processor(f'{self._save_file_path}_{int(time.time() * 1000)}')

        if self._clear_input_buffer_after_training:
            super()._clear_input_buffer()
            return
        if self._process_input_buffer_after_training:
            super()._process_input_buffer()
            return

    @abc.abstractmethod
    def _train(self, data: FrameworkData, label: FrameworkData):
        raise NotImplementedError()

    def _is_training_condition_satisfied(self) -> bool:
        return self._input_buffer[self.INPUT_DATA].get_data_count() >= self.training_set_size \
               and self._input_buffer[self.INPUT_LABEL].get_data_count() >= self.training_set_size

    def _is_processing_condition_satisfied(self) -> bool:
        return self._input_buffer[self.INPUT_DATA].get_data_count() > 0

    @abc.abstractmethod
    def _should_retrain(self) -> bool:
        raise NotImplementedError()

    def _get_inputs(self) -> List[str]:
        return [
            self.INPUT_DATA,
            self.INPUT_LABEL
        ]
