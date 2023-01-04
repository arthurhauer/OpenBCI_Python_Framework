import abc
from typing import Final, Any

from sklearn.base import TransformerMixin, BaseEstimator
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

from models.framework_data import FrameworkData
from models.node.processing.trainable.classifier.sklearn_classifier import SKLearnClassifier


class LDA(SKLearnClassifier):
    _MODULE_NAME: Final[str] = 'node.processing.trainable.classifier.lda'

    @abc.abstractmethod
    def _validate_parameters(self, parameters: dict):
        super()._validate_parameters(parameters)

    def _initialize_parameter_fields(self, parameters: dict):
        super()._initialize_parameter_fields(parameters)

    def _initialize_trainable_processor(self) -> (TransformerMixin, BaseEstimator):
        return LinearDiscriminantAnalysis()

    @abc.abstractmethod
    def _should_retrain(self) -> bool:
        return False

    @abc.abstractmethod
    def _is_next_node_call_enabled(self) -> bool:
        return True

    def _format_processed_data(self, processed_data: Any, sampling_frequency: float) -> FrameworkData:
        formatted_data = FrameworkData(sampling_frequency_hz=sampling_frequency)
        formatted_data.input_data_on_channel(processed_data)
        return formatted_data
