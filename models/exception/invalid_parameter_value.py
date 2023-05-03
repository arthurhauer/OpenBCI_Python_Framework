from models.exception.framework_base_exception import FrameworkBaseException


class InvalidParameterValue(FrameworkBaseException):
    """
    Exception for invalid parameter value. This exception is used when a parameter value is invalid.
    """
    def __init__(self, module: str, name: str, parameter: str, cause: str):
        super().__init__(exception_type='invalid.parameter.value', module=module, name=name)
        self.message: str = f'{self.message}.{parameter}.{cause}'

    def __str__(self):
        return self.message
