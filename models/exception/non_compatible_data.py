from models.exception.framework_base_exception import FrameworkBaseException


class NonCompatibleData(FrameworkBaseException):
    def __init__(self, module: str, name: str, cause: str = None):
        super().__init__(exception_type='non.compatible.data', module=module, name=name)
        if cause is not None:
            self.message = f'{self.message}.{cause}'
