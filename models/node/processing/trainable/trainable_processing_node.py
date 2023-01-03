import abc
from typing import Final, List

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode


class TrainableProcessingNode(ProcessingNode):
    _MODULE_NAME: Final[str] = 'models.node.processing.trainable'

    INPUT_DATA: Final[str] = 'data'
    INPUT_LABEL: Final[str] = 'label'

    def __init__(self, parameters: dict) -> None:
        super().__init__(parameters=parameters)
        self._clear_input_buffer_after_training: bool = parameters['buffer_options'][
            'clear_input_buffer_after_training']
        self._process_input_buffer_after_training: bool = False \
            if parameters['buffer_options']['clear_input_buffer_after_training'] \
            else parameters['buffer_options']['process_input_buffer_after_training']
        self._is_trained: bool = False

    @abc.abstractmethod
    def _validate_parameters(self, parameters: dict):
        super()._validate_parameters(parameters)
        if 'clear_input_buffer_after_training' not in parameters['buffer_options']:
            raise MissingParameterError(module=self._MODULE_NAME,
                                        parameter='buffer_options.clear_input_buffer_after_training')
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

        if self._clear_input_buffer_after_training:
            super()._clear_input_buffer()
            return
        if self._process_input_buffer_after_training:
            super()._process_input_buffer()
            return

    @classmethod
    @abc.abstractmethod
    def from_config_json(cls, parameters: dict):
        raise NotImplementedError()

    @abc.abstractmethod
    def _train(self, data: FrameworkData, label: FrameworkData):
        raise NotImplementedError()

    @abc.abstractmethod
    def _is_training_condition_satisfied(self) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def _should_retrain(self) -> bool:
        raise NotImplementedError()

    def _get_inputs(self) -> List[str]:
        return [
            self.INPUT_DATA,
            self.INPUT_LABEL
        ]
