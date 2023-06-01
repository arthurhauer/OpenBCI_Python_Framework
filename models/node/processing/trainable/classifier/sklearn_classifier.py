import abc
from typing import Final, Any

import numpy as np
from sklearn.base import TransformerMixin, BaseEstimator

from models.framework_data import FrameworkData
from models.node.processing.trainable.sklearn_compatible_trainable_node import SKLearnCompatibleTrainableNode


class SKLearnClassifier(SKLearnCompatibleTrainableNode):
    """ Base class for all SKLearn classifiers. This node is just a serie of methods that need to be implemented
    by the node that will extend this class.

    Attributes:
        _MODULE_NAME (str): The name of the module(in this case ``node.processing.trainable.classifier``)
    """
    _MODULE_NAME: Final[str] = 'node.processing.trainable.classifier.sklearn_classifier'

    @abc.abstractmethod
    def _initialize_parameter_fields(self, parameters: dict):
        super()._initialize_parameter_fields(parameters)

    @abc.abstractmethod
    def _validate_parameters(self, parameters: dict):
        super()._validate_parameters(parameters)

    @abc.abstractmethod
    def _initialize_trainable_processor(self) -> (TransformerMixin, BaseEstimator):
        raise NotImplementedError()

    @abc.abstractmethod
    def _should_retrain(self) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def _is_next_node_call_enabled(self) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def _format_processed_data(self, processed_data: Any, sampling_frequency: float) -> FrameworkData:
        raise NotImplementedError()

    def _inner_process_data(self, data: Any) -> Any:
        return self.sklearn_processor.predict(data)
