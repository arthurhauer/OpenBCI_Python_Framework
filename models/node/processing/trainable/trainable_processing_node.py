import abc
from typing import Final

from models.exception.missing_parameter import MissingParameterError
from models.node.processing.processing_node import ProcessingNode


class TrainableProcessingNode(ProcessingNode):
    _MODULE_NAME: Final[str] = 'models.node.processing.trainable'

    _clear_input_buffer_after_training: bool
    _is_trained: bool

    def __init__(self, parameters: dict) -> None:
        super().__init__(parameters=parameters)

    @abc.abstractmethod
    def _validate_parameters(self, parameters: dict):
        super()._validate_parameters(parameters)
        if 'clear_input_buffer_after_training' not in parameters['buffer_options']:
            raise MissingParameterError(module=self._MODULE_NAME,
                                        parameter='buffer_options.clear_input_buffer_after_training')
        if parameters['buffer_options']['clear_input_buffer_after_training'] is False \
                and 'process_input_buffer_after_training' not in parameters['buffer_options']:
            raise MissingParameterError(module=self._MODULE_NAME,
                                        parameter='buffer_options.process_input_buffer_after_training')

    def _process_input_buffer(self):
        if self._is_trained:
            super()._process_input_buffer()
            return
        if not self._is_training_condition_satisfied():
            return

        self._train(super()._input_buffer)
        self._is_trained = True

        if self._clear_input_buffer_after_training:
            super()._clear_input_buffer()
        else:
            super()._process_input_buffer()

    @classmethod
    @abc.abstractmethod
    def from_config_json(cls, parameters: dict):
        raise NotImplementedError()

    @abc.abstractmethod
    def _train(self, data: list):
        raise NotImplementedError()

    @abc.abstractmethod
    def _is_training_condition_satisfied(self) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def _should_retrain(self) -> bool:
        raise NotImplementedError()
