from models.preprocessing.processor import Processor


class Custom(Processor):

    def __init__(self,parameters:dict) -> None:
        super().__init__()