from models.exception.framework_base_exception import FrameworkBaseException


class NonCompatibleData(FrameworkBaseException):
    def __init__(self, module: str, cause: str = None):
        super().__init__(exception_type='non.compatible.data', module=module)
        if cause is not None:
            self.message = f'{self.message}.{cause}'
