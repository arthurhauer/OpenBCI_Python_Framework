import abc
import csv
import os
from typing import List, Final, Dict

from serial import SerialBase, Serial, SerialException

from models.exception.framework_base_exception import FrameworkBaseException
from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.output.output_node import OutputNode


class SerialOutputNode(OutputNode):
    """ This abstract node is used to connect to an serial device and communicate with it, implementing read, write and
        connect methods altogether
    Attributes:
        _MODULE_NAME (str): The name of the module (in this case, ``node.output.device.serial.serial_output_node``).

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
    """
    _MODULE_NAME: Final[str] = 'node.output.device.serial.serial_output_node'

    def _validate_parameters(self, parameters: dict):
        super()._validate_parameters(parameters)
        if 'communication' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='communication')
        if 'encoding' not in parameters['communication']:
            parameters['communication']['encoding'] = 'UTF-8'

        if 'termination' not in parameters['communication']:
            parameters['communication']['termination'] = '\n'

        if 'serial_port' not in parameters['communication']:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='communication.serial_port')
        if 'baud_rate' not in parameters['communication']:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='communication.baud_rate')
        if 'byte_size' not in parameters['communication']:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='communication.byte_size')
        if 'parity' not in parameters['communication']:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='parity')
        if 'stop_bits' not in parameters['communication']:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='communication.stop_bits')
        if type(parameters['communication']) is not dict:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='communication',
                                        cause='must_be_dict')
        if type(parameters['communication']['serial_port']) is not str:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='communication.serial_port',
                                        cause='must_be_str')
        if type(parameters['communication']['encoding']) is not str:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='communication.encoding',
                                        cause='must_be_str')
        if type(parameters['communication']['termination']) is not str:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='communication.termination_char',
                                        cause='must_be_str')
        if type(parameters['communication']['baud_rate']) is not int:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='communication.baud_rate',
                                        cause='must_be_int')
        if type(parameters['communication']['byte_size']) is not int:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='communication.byte_size',
                                        cause='must_be_int')
        if parameters['communication']['byte_size'] not in SerialBase.BYTESIZES:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='communication.byte_size',
                                        cause=f'must_be_between_one_of_[{SerialBase.BYTESIZES}]')
        if type(parameters['communication']['parity']) is not str:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='communication.parity',
                                        cause='must_be_str')
        if parameters['communication']['parity'] not in SerialBase.PARITIES:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='communication.byte_size',
                                        cause=f'must_be_between_one_of_[{SerialBase.PARITIES}]')
        if type(parameters['communication']['stop_bits']) is not float and type(parameters['communication']['stop_bits']) is not int:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='communication.stop_bits',
                                        cause='must_be_float')
        if parameters['communication']['stop_bits'] not in SerialBase.STOPBITS:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='communication.stop_bits',
                                        cause=f'must_be_between_one_of_[{SerialBase.STOPBITS}]')

    def _initialize_parameter_fields(self, parameters: dict):
        super()._initialize_parameter_fields(parameters)
        self._serial_session = Serial(port=parameters['communication']['serial_port'],
                                      baudrate=parameters['communication']['baud_rate'],
                                      bytesize=parameters['communication']['byte_size'],
                                      parity=parameters['communication']['parity'],
                                      stopbits=parameters['communication']['stop_bits'])
        try:
            self._serial_session.open()
        except SerialException as e:
            fw_exception = FrameworkBaseException(exception_type='serial.open',
                                                  module=self._MODULE_NAME,
                                                  name=self.name)
            fw_exception.message += f'[{e}]'
            raise fw_exception
        self._encoding = parameters['communication']['encoding']
        self._termination = parameters['communication']['termination'].encode(self._encoding)

    def _write(self, data: bytes) -> None:
        try:
            self._serial_session.write(data + self._termination)
        except SerialException as e:
            fw_exception = FrameworkBaseException(exception_type='serial.write',
                                                  module=self._MODULE_NAME,
                                                  name=self.name)
            fw_exception.message += f'[{e}]'
            raise fw_exception

    def _read(self) -> bytes:
        try:
            return self._serial_session.read_until(self._termination)
        except SerialException as e:
            fw_exception = FrameworkBaseException(exception_type='serial.read',
                                                  module=self._MODULE_NAME,
                                                  name=self.name)
            fw_exception.message += f'[{e}]'
            raise fw_exception

    @abc.abstractmethod
    def _process(self, data: Dict[str, FrameworkData]) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def _is_processing_condition_satisfied(self) -> bool:
        return True

    @abc.abstractmethod
    def _get_inputs(self) -> List[str]:
        raise NotImplementedError()

    def dispose(self) -> None:
        self._serial_session.close()
        super().dispose()
