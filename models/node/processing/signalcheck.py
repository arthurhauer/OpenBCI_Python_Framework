from models.node.processing.processing_node import ProcessingNode


class SignalCheck(ProcessingNode):

    def __init__(self, parameters: dict) -> None:
        super().__init__(parameters)

    @classmethod
    def from_config_json(cls, parameters: dict):
        return cls(parameters)

    def _is_next_node_call_enabled(self) -> bool:
        return True

    def _is_processing_condition_satisfied(self) -> bool:
        # TODO change
        return len(self._input_buffer) > 0

    def _process(self, data: list) -> list:
        # TODO change
        print('SignalCheck!')
        return data
