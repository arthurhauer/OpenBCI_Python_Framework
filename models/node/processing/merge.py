from typing import List, Dict, Final

from models.node.processing.processing_node import ProcessingNode


# TODO implementar
class Merge(ProcessingNode):
    _MODULE_NAME: Final[str] = 'node.processing.merge'

    INPUT_MASTER_MAIN: Final[str] = 'master_main'
    INPUT_MASTER_TIMESTAMP: Final[str] = 'master_timestamp'
    INPUT_SLAVE_MAIN: Final[str] = 'slave_timestamp'
    INPUT_SLAVE_TIMESTAMP: Final[str] = 'slave_timestamp'
    OUTPUT_MERGED_MAIN: Final[str] = 'merged_main'
    OUTPUT_MERGED_TIMESTAMP: Final[str] = 'merged_timestamp'

    def __init__(self, parameters: dict):
        super().__init__(parameters)

    @classmethod
    def from_config_json(cls, parameters: dict):
        pass

    def _is_next_node_call_enabled(self) -> bool:
        pass

    def _is_processing_condition_satisfied(self) -> bool:
        pass

    def _process(self, data: Dict[str, list]) -> Dict[str, list]:
        pass

    def _get_inputs(self) -> List[str]:
        return [
            self.INPUT_MASTER_MAIN,
            self.INPUT_MASTER_TIMESTAMP,
            self.INPUT_SLAVE_MAIN,
            self.INPUT_SLAVE_TIMESTAMP,
        ]

    def _get_outputs(self) -> List[str]:
        return [
            self.OUTPUT_MERGED_MAIN,
            self.OUTPUT_MERGED_TIMESTAMP
        ]
