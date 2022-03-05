import os
from typing import Dict, Any


def script_execute(script_path: str) -> Dict[str, Any]:
    if not os.path.isfile(script_path):
        raise ValueError('utils.script_execute.file.doesnt.exist.%s' % script_path)
    # Open and read the given custom python script
    file = open(script_path, 'r')
    script = file.read()
    # Compile the script
    compiled_script = compile(script, '', 'exec')
    _locals = locals()
    # Execute the script, setting _locals dict
    exec(compiled_script, _locals)
    return _locals
