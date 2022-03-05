class Channel:

    def __init__(self, name: str, show: bool = True) -> None:
        super().__init__()
        self.name = name
        self.show = show

    @classmethod
    def from_config_json(cls, parameters: dict):
        if 'name' not in parameters:
            raise Exception('channel.must.have.name')
        if 'show' not in parameters:
            parameters['show'] = True
        return cls(parameters['name'], parameters['show'])