import abc


class PreProcessingNode:
    _action = lambda data: None
    _type: str

    def __init__(self, parameters: dict) -> None:
        super().__init__()
        if 'type' not in parameters:
            raise Exception('preprocessing.node.invalid.parameters.must.have.type')
        self._type = parameters['type']

    @abc.abstractmethod
    def process(self, data):
        raise NotImplementedError()
        # return self._action(data)
