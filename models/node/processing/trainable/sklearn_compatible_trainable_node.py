import abc
from typing import List, Dict, Final, Any

import numpy as np
from sklearn.base import TransformerMixin, BaseEstimator

from models.framework_data import FrameworkData
from models.node.processing.trainable.trainable_processing_node import TrainableProcessingNode


class SKLearnCompatibleTrainableNode(TrainableProcessingNode):
    _MODULE_NAME: Final[str] = 'node.processing.trainable.sklearn_compatible_trainable_node'

    OUTPUT_MAIN: Final[str] = 'main'

    @abc.abstractmethod
    def _validate_parameters(self, parameters: dict):
        super()._validate_parameters(parameters)

    @abc.abstractmethod
    def _initialize_parameter_fields(self, parameters: dict):
        super()._initialize_parameter_fields(parameters)
        self.sklearn_processor: (TransformerMixin, BaseEstimator) = self._initialize_trainable_processor()

    @abc.abstractmethod
    def _initialize_trainable_processor(self) -> (TransformerMixin, BaseEstimator):
        raise NotImplementedError()

    @classmethod
    def from_config_json(cls, parameters: dict):
        return cls(parameters)

    @abc.abstractmethod
    def _should_retrain(self) -> bool:
        raise NotImplementedError()

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        raw_data: Any = self._format_raw_data(data[self.INPUT_DATA])
        processed_data: Any = self._inner_process_data(raw_data)
        return {
            self.OUTPUT_MAIN: self._format_processed_data(processed_data, data[self.INPUT_DATA].sampling_frequency)
        }

    def _format_raw_data(self, raw_data: FrameworkData) -> Any:
        formatted_data = np.asarray(raw_data.get_data_as_2d_array())
        formatted_data = np.moveaxis(formatted_data, 1, 0)
        return formatted_data

    def _format_raw_label(self, raw_label: FrameworkData) -> Any:
        formatted_label = []
        for epoch in raw_label.get_data_single_channel():
            formatted_label.append(max(epoch))
        formatted_label = np.asarray(formatted_label)
        return formatted_label

    @abc.abstractmethod
    def _format_processed_data(self, processed_data: Any, sampling_frequency: float) -> FrameworkData:
        raise NotImplementedError()

    @abc.abstractmethod
    def _inner_process_data(self, data: Any) -> Any:
        raise NotImplementedError()

    def _inner_train_processor(self, data: Any, label: Any):
        return self.sklearn_processor.fit(data, label)

    def _train(self, data: FrameworkData, label: FrameworkData):
        formatted_data = self._format_raw_data(data)
        formatted_label = self._format_raw_label(label)
        self._inner_train_processor(formatted_data[0:self.training_set_size], formatted_label[0:self.training_set_size])

    @abc.abstractmethod
    def _is_next_node_call_enabled(self) -> bool:
        super()._is_next_node_call_enabled()

    @abc.abstractmethod
    def _get_outputs(self) -> List[str]:
        return [
            self.OUTPUT_MAIN
        ]
