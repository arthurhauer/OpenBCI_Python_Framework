from models.exception.framework_base_exception import FrameworkBaseException


class NonCompatibleData(FrameworkBaseException):
    """
    Exception for non compatible data. This exception is used when a data is not compatible with the expected data.
    """
    def __init__(self, module: str, name: str, cause: str = None):
        super().__init__(exception_type='non.compatible.data', module=module, name=name)
        if cause is not None:
            self.message = f'{self.message}.{cause}'
