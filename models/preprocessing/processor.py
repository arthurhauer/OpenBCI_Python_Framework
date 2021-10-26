import abc


class Processor:
    _action = lambda data: None
    _type: str

    def __init__(self, parameters: dict) -> None:
        super().__init__()
        if 'type' not in parameters:
            raise Exception('preprocessing.processor.invalid.parameters.must.have.type')
        self._type = parameters['type']

    def process(self, data):
        return self._action(data)
