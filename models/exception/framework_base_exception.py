class FrameworkBaseException(Exception):
    def __init__(self, exception_type: str, module: str, *args):
        super().__init__()
        self.message: str = f'error.{exception_type}.{module}'

    def __str__(self):
        return self.message
