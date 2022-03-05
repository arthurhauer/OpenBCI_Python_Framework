import os.path

from globals.globals import CUSTOMS_DIR
from models.data.processing.processing_node import ProcessingNode
from models.utils.utils import script_execute


class Custom(ProcessingNode):

    def __init__(self, process, process_parameters) -> None:
        super().__init__()
        if process is None:
            raise ValueError('preprocessing.custom.invalid.process.None')
        if process_parameters is None:
            self._parameters = {}
        else:
            self._parameters = process_parameters
        self._custom_process = process

    @classmethod
    def from_config_json(cls, parameters: dict):
        if 'file' not in parameters:
            raise ValueError('preprocessing.custom.invalid.parameters.must.have.file')
        custom_script_path = os.path.join(CUSTOMS_DIR, parameters['file'])
        _locals = script_execute(custom_script_path)

        if 'custom_process' not in _locals:
            raise ValueError(
                'preprocessing.custom.invalid.parameters.custom_process.not.defined.in.script.%s' % custom_script_path)

        if 'process-parameters' not in parameters:
            process_parameters = {}
        else:
            process_parameters = parameters['process-parameters']
        return cls(
            process=_locals['custom_process'],
            process_parameters=process_parameters
        )

    def process(self, data):
        # Call the function set in the constructor
        self._custom_process(self._parameters, data)
