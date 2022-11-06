import threading
from typing import Final

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.utils.cue import Cue
from models.utils.duration import Duration


class Trial:
    _MODULE_NAME: Final[str] = 'utils.trial'

    def __init__(self, name: str, code: int, duration: Duration, cue: Cue) -> None:
        super().__init__()
        if name is None:
            raise MissingParameterError(module=self._MODULE_NAME,
                                        parameter='name')
        if code is None:
            raise MissingParameterError(module=self._MODULE_NAME,
                                        parameter='code')
        if len(name) == 0:
            raise InvalidParameterValue(module=self._MODULE_NAME,
                                        parameter='name',
                                        cause='len==0')
        if duration is None:
            raise MissingParameterError(module=self._MODULE_NAME,
                                        parameter='duration')
        if cue is None:
            raise MissingParameterError(module=self._MODULE_NAME,
                                        parameter='cue')
        self.name = name
        self.code = code
        self.duration = duration
        self.cue = cue

    @classmethod
    def from_config_json(cls, parameters: dict):
        if 'name' not in parameters:
            raise MissingParameterError(module=cls._MODULE_NAME,
                                        parameter='name')
        if 'code' not in parameters:
            raise MissingParameterError(module=cls._MODULE_NAME,
                                        parameter='code')
        if 'duration' not in parameters:
            raise MissingParameterError(module=cls._MODULE_NAME,
                                        parameter='duration')
        if 'cue' not in parameters:
            raise MissingParameterError(module=cls._MODULE_NAME,
                                        parameter='cue')
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
