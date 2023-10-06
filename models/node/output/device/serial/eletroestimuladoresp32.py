import json
import statistics

import math
from typing import List, Final, Dict, Any

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.output.device.serial.serial_output_node import SerialOutputNode


class EletroEstimuladorESP32(SerialOutputNode):
    """ This node is used to connect to an ESP32, developed by LeNeR Lab in UEL, which controls an Electric Stimulator.
    This node only outputs commands if the previous trigger condition evaluation result differs from the current,
    in order to avoid flooding the device with unnecessary messages.

    Attributes:
        _MODULE_NAME (str): The name of the module (in this case, ``node.output.device.serial.eletroestimuladorESP32``).

    ``configuration.json`` usage:

        **module** (*str*): Current module name (in this case ``node.output.device.serial.serial_output_node``).\n
        **type** (*str*): Current node type (in this case ``SerialOutputNode``).\n
        **communication** (*dict*): Serial communication parameters.\n
            **encoding** (*str*): message encoding, e.g. UTF-8, etc (default: ``"UTF-8"``).\n
            **termination** (*str*): message termination, e.g. \\r\\n, etc (default: ``"\\n"``).\n
            **serial_port** (*str*): serial port, e.g. COM4, /dev/ttyACM0, etc (default: ``""``).\n
            **baud_rate** (*str*): baud rate, e.g. 11520 (default: ``""``).\n
            **byte_size** (*str*): byte size, in bits (5, 6, 7, 8), e.g. 8 (default: ``""``).\n
            **parity** (*str*): parity, (None=N, Even=E, Odd=O, Mark=M, Space=S) e.g. N (default: ``""``).\n
            **stop_bits** (*str*): stop bits (1, 1.5, 2), e.g. 1, /dev/ttyACM0, etc (default: ``""``).\n
        **condition** (*str*): python expression for evaluating when trigger should be ON or OFF. The only variable
        used in the expression should be ``condition_data``. ``math`` and ``statistics`` modules are available. Must be
        an one-line expression that results in a bool output, e.g.
        ``"statistics.mean(condition_data.get_data_single_channel())>0.5"``\n

        .. code-block::

        "electric_stimulator": {
                "module": "models.node.output.device.serial",
                "type": "EletroEstimuladorESP32",
                "condition": "statistics.mean(condition_data.get_data_single_channel())>0.5",
                "communication":{
                    "encoding":"UTF-8",
                    "termination":"\\n",
                    "serial_port":"COM4",
                    "baud_rate": 11520,
                    "byte_size": 8,
                    "parity": "N",
                    "stop_bits": 1
                },
                "buffer_options": {
                  "clear_output_buffer_on_data_input": true,
                  "clear_input_buffer_after_process": true,
                  "clear_output_buffer_after_process": true
                }
              }

    """

    _MODULE_NAME: Final[str] = 'node.output.device.serial.eletroestimuladorESP32'

    INPUT_MAIN: Final[str] = 'main'

    def _validate_parameters(self, parameters: dict):
        super()._validate_parameters(parameters)
        if 'condition' not in parameters:
            raise MissingParameterError(
                module=self._MODULE_NAME, name=self.name,
                parameter='condition'
            )
        if type(parameters['condition']) is not str:
            raise InvalidParameterValue(
                module=self._MODULE_NAME, name=self.name,
                parameter='condition',
                cause='must_be_str'
            )

    def _initialize_parameter_fields(self, parameters: dict):
        super()._initialize_parameter_fields(parameters)
        self._condition_script = parameters['condition']
        self._condition = compile(f'condition_result={self._condition_script}', '', 'exec')
        self._last_trigger_value = False

    def _is_processing_condition_satisfied(self) -> bool:
        return True

    def _evaluate_trigger_condition(self, data: FrameworkData) -> bool:
        local_variables: Dict[str, Any] = {"condition_data": data, "math": math, "statistics": statistics}
        exec(self._condition, globals(), local_variables)
        condition_result: bool = local_variables['condition_result']
        if type(condition_result) is not bool:
            raise InvalidParameterValue(
                module=self._MODULE_NAME,
                name=self.name,
                parameter='condition',
                cause='must_return_bool'
            )
        return condition_result

    def _build_set_trigger_command(self, trigger_value: bool) -> bytes:
        trigger = 1 if trigger_value else 0
        msg = json.dumps({"cmd": "write", "variable": "trigger", "value": trigger})
        return msg.encode(self._encoding)

    def _build_get_trigger_command(self) -> bytes:
        msg = json.dumps({"cmd": "read", "variable": "trigger"})
        return msg.encode(self._encoding)

    def _process(self, data: Dict[str, FrameworkData]) -> None:
        input_data = data[self.INPUT_MAIN]

        trigger = self._evaluate_trigger_condition(input_data)

        if trigger == self._last_trigger_value:
            return

        command = self._build_set_trigger_command(trigger)
        self.print(f'Setting trigger to {trigger}')
        self._write(command)

    def _get_inputs(self) -> List[str]:
        return [
            self.INPUT_MAIN
        ]

    def dispose(self) -> None:
        super().dispose()
