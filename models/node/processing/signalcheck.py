from typing import List, Final

from models.node.processing.processing_node import ProcessingNode


class SignalCheck(ProcessingNode):
    INPUT_MAIN: Final[str] = 'main'
    OUTPUT_MAIN: Final[str] = 'main'

    def __init__(self, parameters: dict) -> None:
        super().__init__(parameters)

    @classmethod
    def from_config_json(cls, parameters: dict):
        return cls(parameters)

    def _is_next_node_call_enabled(self) -> bool:
        return True

    def _is_processing_condition_satisfied(self) -> bool:
        # TODO change
        return True

    def _process(self, data: list) -> list:
        # TODO change
        print('SignalCheck!')
        return data

    def _get_inputs(self) -> List[str]:
        return [
            self.INPUT_MAIN,
            self.INPUT_MAIN2
        ]

    def _get_outputs(self) -> List[str]:
        return [
            self.OUTPUT_MAIN
        ]
