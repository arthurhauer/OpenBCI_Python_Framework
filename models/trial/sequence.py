import threading

from models.trial.cue import Cue
from models.trial.duration import Duration


class Sequence:
    def __init__(self, name: str, code: int, duration: Duration, cue: Cue) -> None:
        super().__init__()
        if name is None:
            raise ValueError('trial.sequence.must.have.name')
        if code is None:
            raise ValueError('trial.sequence.must.have.code')
        if len(name) == 0:
            raise ValueError('trial.sequence.name.must.not.be.empty')
        if duration is None:
            raise ValueError('trial.sequence.must.have.duration')
        if cue is None:
            raise ValueError('trial.sequence.must.have.cue')
        self.name = name
        self.code = code
        self.duration = duration
        self.cue = cue

    @classmethod
    def from_config_json(cls, parameters: dict):
        if 'name' not in parameters:
            raise ValueError('trial.sequence.must.have.name')
        if 'code' not in parameters:
            raise ValueError('trial.sequence.must.have.code')
        if 'duration' not in parameters:
            raise ValueError('trial.sequence.must.have.duration')
        if 'cue' not in parameters:
            raise ValueError('trial.sequence.must.have.cue')
        return cls(
            name=parameters['name'],
            code=parameters['code'],
            duration=Duration.from_config_json(parameters['duration']),
            cue=Cue.from_config_json(parameters['cue'])
        )

    def start(self):
        self.cue.execute()
        timer = threading.Timer(self.duration.get_duration(), self.on_stop)
        timer.start()

    def on_stop(self):
        pass
