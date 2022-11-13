from models.exception.framework_base_exception import FrameworkBaseException


class NonCompatibleData(FrameworkBaseException):
    def __init__(self, module: str):
        super().__init__(exception_type='non.compatible.data', module=module)
