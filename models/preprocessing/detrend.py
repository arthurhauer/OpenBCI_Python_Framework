class Detrend:
    def __init__(self, parameters: dict) -> None:
        super().__init__()
        if parameters['type'] is None:
            raise Exception('preprocessing.detrend.invalid.parameters.must.have.type')
        
