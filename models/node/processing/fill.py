from typing import List, Dict, Final

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.processing.processing_node import ProcessingNode


class Fill(ProcessingNode):
    """ This node is used to fill the input buffer with a certain amount of samples. This is useful when the input buffer
    is not filled with the desired amount of samples. This node can fill the input buffer with zeros or with the last
    sample in the input buffer.

    Attributes:
        _MODULE_NAME (str): The name of the module(in this case ``node.processing.fill``)
        INPUT_MAIN (str): The name of the main input(in this case ``main``)
        OUTPUT_MAIN (str): The name of the main output(in this case ``main``)
        FILL_TYPE_ZEROFILL (str): The name of the fill type that fills the input buffer with zeros(in this case ``zero_fill``)
        FILL_TYPE_SAMPLE_AND_HOLD (str): The name of the fill type that fills the input buffer with the last sample(in this case ``sample_and_hold``)

    configuration.json usage:
        **module** (*str*): The name of the module (``node.processing.fill``)\n
        **type** (*str*): The name of the class (``Fill``)\n
        **fill_size** (*int*): The size of the input buffer after filling.\n
        **filling_type** (*str*): The type of filling to use. Can be ``zero_fill`` or ``sample_and_hold``.\n
        **buffer_options** (*dict*): Buffer options.\n
            **clear_output_buffer_after_process** (*bool*): Whether to clear the output buffer after processing.\n
            **clear_input_buffer_after_process** (*bool*): Whether to clear the input buffer after processing.\n
            **clear_output_buffer_on_data_input** (*bool*): Whether to clear the output buffer when new data is inserted in the input buffer.\n

    """
    _MODULE_NAME: Final[str] = 'node.processing.fill'

    INPUT_MAIN: Final[str] = 'main'
    OUTPUT_MAIN: Final[str] = 'main'

    FILL_TYPE_ZEROFILL: Final[str] = 'zero_fill'
    FILL_TYPE_SAMPLE_AND_HOLD: Final[str] = 'sample_and_hold'

    def _validate_parameters(self, parameters: dict):
        """ Validate the parameters passed to the node. This method will raise an exception if the parameters are not
        valid or when they don't exist.

        :param parameters: The parameters passed to the node.
        :type parameters: dict

        :raises MissingParameterError: the ``full_size`` parameter is required.
        :raises InvalidParameterValue: the ``fill_size`` parameter must be an integer.
        :raises MissingParameterError: the ``filling_type`` parameter is required.
        :raises InvalidParameterValue: the ``filling_type`` parameter must be ``zero_fill`` or ``sample_and_hold``.
        """

        if 'fill_size' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='fill_size')
        if 'filling_type' not in parameters:
            raise MissingParameterError(module=self._MODULE_NAME, name=self.name,
                                        parameter='filling_type')

        if type(parameters['fill_size']) is not int:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='fill_size',
                                        cause='must_be_int')

        if parameters['filling_type'] not in [self.FILL_TYPE_ZEROFILL, self.FILL_TYPE_SAMPLE_AND_HOLD]:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='filling_type',
                                        cause=f'not_in_[{self.FILL_TYPE_ZEROFILL},{self.FILL_TYPE_SAMPLE_AND_HOLD}]')

    def _initialize_parameter_fields(self, parameters: dict):
        """ Initialize the parameter fields of the node. This method will set the ``_fill_size`` and ``_fill_type``
        attributes and  all the parent attributes as well.

        :param parameters: The parameters passed to the node.
        :type parameters: dict
        """
        super()._initialize_parameter_fields(parameters)
        self._zero_fill = parameters['filling_type'] == self.FILL_TYPE_ZEROFILL
        self._sample_and_hold = parameters['filling_type'] == self.FILL_TYPE_SAMPLE_AND_HOLD
        self._fill_size: int = parameters['fill_size']

    def _is_next_node_call_enabled(self) -> bool:
        """ This method will return ``True`` if the next node call is enabled. This method will always return ``True``
        because the next node call is always enabled.
        """
        return True

    def _is_processing_condition_satisfied(self) -> bool:
        """ This method will return ``True`` if the processing condition is satisfied. This method will return ``True``
        if the input buffer has data.

        :return: ``True`` if the input buffer has data, ``False`` otherwise.
        :rtype: bool
        """
        return self._input_buffer[self.INPUT_MAIN].get_data_count() > 0

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        """ This method will process the data in the input buffer and return the result in the output buffer. This
        method will fill the input buffer with a certain amount of samples. This is done using the _fill method.

        :param data: The data to process.
        :type data: dict

        :return: The processed data.
        :rtype: dict
        """
        slave_main = data[self.INPUT_MAIN]

        new_data = FrameworkData(sampling_frequency_hz=slave_main.sampling_frequency,
                                 channels=slave_main.channels)

        for data_index, data_value in enumerate(slave_main.get_data_as_2d_array()[0]):
            new_data.extend(
                self._fill(
                    data_index,
                    slave_main,
                    new_data.sampling_frequency
                )
            )
        return {
            self.OUTPUT_MAIN: new_data
        }

    def _get_inputs(self) -> List[str]:
        """ This method will return the inputs of the node.
        
        :return: The inputs of the node.
        :rtype: list
        """
        return [
            self.INPUT_MAIN,
        ]

    def _get_outputs(self) -> List[str]:
        """ This method will return the outputs of the node.
        
        :return: The outputs of the node.
        :rtype: list
        """
        return [
            self.OUTPUT_MAIN
        ]

    def _fill(self,
              data_index: int,
              slave_main: FrameworkData,
              sampling_frequency: float) -> FrameworkData:
        """ This method will fill the input buffer with a certain amount of samples with the desired filling type. This filling
        type can be ``zero_fill`` or ``sample_and_hold``. If the filling type is ``zero_fill`` the input buffer will be filled
        with zeros. If the filling type is ``sample_and_hold`` the input buffer will be filled with the last sample in the
        input buffer.

        :param data_index: The index of the data to fill.
        :type data_index: int
        :param slave_main: The INPUT_MAIN data.
        :type slave_main: FrameworkData
        :param sampling_frequency: The sampling frequency of the data to fill.
        :type sampling_frequency: float

        :return: The filled data.
        :rtype: FrameworkData
        """
        fill_data = FrameworkData(sampling_frequency, slave_main.channels)

        if self._zero_fill:
            channel_data = [0] * self._fill_size
            input_data = [channel_data] * len(slave_main.channels)
            fill_data.input_2d_data(input_data)
        elif self._sample_and_hold:
            input_data = slave_main.get_data_at_index(data_index)
            for channel in input_data:
                channel_data = [input_data[channel]] * self._fill_size
                fill_data.input_data_on_channel(channel_data, channel)
        else:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='filling_type',
                                        cause='not_set')

        return fill_data
