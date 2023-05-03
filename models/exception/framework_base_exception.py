class FrameworkBaseException(Exception):
    """
    Base exception for all framework exceptions.
    """
    def __init__(self, exception_type: str, module: str, name: str, *args):
        super().__init__()
        self.message: str = f'error.{exception_type}.{module}.{name}'

    def __str__(self):
        return self.message
