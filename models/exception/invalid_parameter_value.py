from models.exception.framework_base_exception import FrameworkBaseException


class InvalidParameterValue(FrameworkBaseException):
    def __init__(self, module: str, parameter: str, cause: str):
        super().__init__(exception_type='invalid.parameter.value', module=module)
        self.message: str = f'{self.message}.{parameter}.{cause}'

    def __str__(self):
        return self.message