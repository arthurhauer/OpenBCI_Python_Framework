from typing import List

from config.configuration import Configuration
from models.preprocessing.node import PreProcessingNode


class PreProcessing:
    __pipeline: List[PreProcessingNode] = None

    def __init__(self) -> None:
        super().__init__()

    @property
    def _pipeline(self):
        if self.__pipeline is None:
            self.__pipeline = []
            for preprocessing_node_settings in Configuration.get_preprocessing_settings():
                self.__pipeline.append(PreProcessingNode(preprocessing_node_settings))
        return self.__pipeline

    def process(self, data):
        for node in self._pipeline:
            node.process(data)
