from models.exception.framework_base_exception import FrameworkBaseException


class MissingParameterError(FrameworkBaseException):
    def __init__(self, module: str, parameter: str):
        super().__init__(exception_type='missing.parameter', module=module)
        self.message: str = f'{self.message}.{parameter}'