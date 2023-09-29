import abc
from typing import Final, Any, List, Dict

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

    OUTPUT_PROBABILITY: Final[str] = 'probability'

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
        class_probabilities: Any = self._get_probability(raw_data)
        sampling_frequency: float = data[self.INPUT_DATA].sampling_frequency
        return {
            self.OUTPUT_MAIN: self._format_processed_data(processed_data, sampling_frequency),
            self.OUTPUT_PROBABILITY: self._format_processed_data(class_probabilities, sampling_frequency)
        }

    def _inner_process_data(self, data: Any) -> Any:
        return self.sklearn_processor.predict(data)

    def _get_probability(self, data: Any) -> Any:
        if not (hasattr(self.sklearn_processor, 'predict_proba') and callable(self.sklearn_processor.predict_proba)):
            return [[]]
        return self.sklearn_processor.predict_proba(data)

    def _get_outputs(self) -> List[str]:
        return [
            self.OUTPUT_MAIN,
            self.OUTPUT_PROBABILITY
        ]
