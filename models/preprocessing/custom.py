import os.path

from globals.globals import CUSTOMS_DIR
from models.preprocessing.node import PreProcessingNode


class Custom(PreProcessingNode):

    def __init__(self, parameters: dict) -> None:
        super().__init__(parameters)
        if 'file' not in parameters:
            raise ValueError('preprocessing.custom.invalid.parameters.must.have.file')
        custom_script_path = os.path.join(CUSTOMS_DIR, parameters['file'])
        if not os.path.isfile(custom_script_path):
            raise ValueError('preprocessing.custom.invalid.parameters.file.doesnt.exist.' + parameters['file'])
        # Setting instance attribute so the compiler won't complain
        self._custom_process = None
        # Open and read the given custom python script
        file = open(custom_script_path, 'r')
        script = file.read()
        # Force instance attribute reference to user script-defined function
        script += '\nself._custom_process = custom_process'
        # Compile the script
        compiled_script = compile(script, '', 'exec')
        # Execute the script, setting self._custom_process
        exec(compiled_script)
        self._parameters = {key: parameters[key] for key in parameters if not key == 'file'}

    def process(self, data):
        # Call the function set in the constructor
        self._custom_process(self._parameters, data)
