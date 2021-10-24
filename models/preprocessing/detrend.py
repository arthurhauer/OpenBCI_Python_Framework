from models.preprocessing.processor import Processor


class Detrend(Processor):
    def __init__(self, parameters: dict) -> None:
        super(Processor).__init__(parameters)
        
