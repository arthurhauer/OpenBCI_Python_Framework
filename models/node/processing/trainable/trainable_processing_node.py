import abc

from models.node.processing.processing_node import ProcessingNode


class TrainableProcessingNode(ProcessingNode):

    _clear_input_buffer_after_training: bool
    _is_trained: bool

    def __init__(self, parameters: dict) -> None:
        super().__init__(parameters=parameters)
        if 'clear_input_buffer_after_training' not in parameters['buffer_options']:
            raise ValueError('error.'
                             'trainableprocessingnode.'
                             'buffer_options.'
                             'clear_input_buffer_after_training.'
                             'missing')

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
