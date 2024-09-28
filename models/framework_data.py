from __future__ import annotations

import copy
from typing import Final, List, Dict
from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.non_compatible_data import NonCompatibleData


class FrameworkData:
    """This class is used to store data in a format that is compatible with the framework.
    It is used to store data that is used by the framework, such as the data that is
    used to train the model, or the data that is used to test the model. It is also
    used to store the data that is output by the model, such as the predictions that
    the model makes, or the data that is used to evaluate the model.

    :param sampling_frequency_hz: The sampling frequency of the data. Defaults to None.
    :param channels: The names of the channels that the data is stored on. Defaults to None.
    :type sampling_frequency_hz: float, optional
    :type channels: List[str], optional

    :raises NonCompatibleData: Raised when the data that is being input is not compatible with the data that is already stored in the ``FrameworkData`` object.
    """

    _MODULE_NAME: Final[str] = 'models.framework_data'
    _DEFAULT_CHANNEL_NAME: Final[str] = 'main'

    def __init__(self, sampling_frequency_hz: float = None, channels: List[str] = None, ):
        if channels is None:
            self._channels_set = None
            self.channels = []
        else:
            self.channels = channels
            self._channels_set = set(self.channels)
        self._init_data_dictionary()
        self.sampling_frequency = sampling_frequency_hz

    @classmethod
    def from_single_channel(cls, sampling_frequency_hz: float, data: list):
        """This method is used to create a ``FrameworkData`` object from a single channel of data.

        :param sampling_frequency_hz: The sampling frequency of the data.
        :param data: The data that is to be stored in the ``FrameworkData`` object.
        :type sampling_frequency_hz: float
        :type data: list

        :return: A ``FrameworkData`` object that contains the data that was input.
        :rtype: FrameworkData
        """

        class_data = cls(
            sampling_frequency_hz,
            [cls._DEFAULT_CHANNEL_NAME]
        )
        class_data.input_data_on_channel(data, cls._DEFAULT_CHANNEL_NAME)
        return class_data

    @classmethod
    def from_multi_channel(cls, sampling_frequency_hz: float, channels: List[str], data: List[list]):
        """This method is used to create a ``FrameworkData`` object from multiple channels of data.

        :param sampling_frequency_hz: The sampling frequency of the data.
        :param channels: The names of the channels that the data is stored on.
        :type sampling_frequency_hz: float
        :type channels: List[str]

        :return: A ``FrameworkData`` object that contains the data that was input.

        :rtype: FrameworkData
        """

        class_data = cls(
            sampling_frequency_hz,
            channels
        )
        class_data.input_2d_data(data)
        return class_data

    def _init_data_dictionary(self):

        """This method is used to initialise the dictionary that is used to store the data.
        For each channel, an empty list is created. The list is used to store the data
        that is input on the channel. The dictionary is created in this class method
        because it is only created once, and it is not created every time that the
        ``FrameworkData`` object is extended. This is because creating a dictionary is a
        computationally expensive operation, and it would be inefficient to create a
        dictionary every time that the ``FrameworkData`` object is extended.

        :param None:

        :return: None
        """

        self._data = {}
        for channel in self.channels:
            self._data[channel] = []

    def rename_channel(self, current_name: str, new_name: str):
        """This method is used to rename a given channel stored in ``FrameworkData``.

        :param current_name: Existing channel key
        :param new_name: Key to replace existing channel key

        :return: None
        :rtype: None
        """
        if current_name not in self.channels:
            raise InvalidParameterValue(module=self._MODULE_NAME, name='data',
                                        parameter='current_name',
                                        cause='must_be_existing_key')
        if new_name in self.channels:
            raise InvalidParameterValue(module=self._MODULE_NAME, name='data',
                                        parameter='new_name',
                                        cause='must_be_non_existing_key')
        self._data[new_name] = self._data[current_name]
        del self._data[current_name]
        self.channels.remove(current_name)
        self.channels.append(new_name)

    def get_data_count(self):
        """This method is used to get the number of data points that are stored in the
        ``FrameworkData`` object. This is normally used to check that the data that is input is
        compatible with the data that is already stored in the ``FrameworkData`` object.

        We only return the first channel length because we have already checked that all 
        channels have the same length. When there is no channels, we return 0

        :param None:

        :return: The number of data points that are stored in the ``FrameworkData`` object.
        :rtype: int
        """

        if len(self.channels) == 0:
            return 0
        return len(self._data[self.channels[0]])

    def get_channels_as_set(self):
        """This method is used to get the channels that the data is stored on as a set. If the
        channels have not been set, then the channels are set to the default channel name,
        and the channels are returned as a set.

        :param None:

        :return: The channels that the data is stored on as a set.
        :rtype: set
        """

        if self._channels_set is None:
            self._channels_set = set(self.channels)
        return self._channels_set

    def extend(self, input_data: FrameworkData):
        """This method is used to extend the ``FrameworkData`` object with the data that is input.
        The data that is input is checked to ensure that it is compatible with the data that
        is already stored in the ``FrameworkData`` object. If the data is compatible, then the
        data is extended. If the data is not compatible, then an exception is raised.

        :param data: The data that is to be extended.
        :type data: ``FrameworkData``

        :raises NonCompatibleData: Raised when the data that is being input is not compatible with the data that is already stored in the ``FrameworkData`` object.

        :return: None
        """
        data = copy.deepcopy(input_data)
        if len(data.channels) == 0:
            return
        if not data.has_data():
            return

        if len(self.channels) == 0:
            self.channels = data.channels
            self.sampling_frequency = data.sampling_frequency
            self._init_data_dictionary()

        elif self.sampling_frequency is not None and data.sampling_frequency is not None and self.sampling_frequency != data.sampling_frequency:
            raise NonCompatibleData(module=self._MODULE_NAME, name='framework_data')
        elif self.get_channels_as_set() != data.get_channels_as_set():
            raise NonCompatibleData(module=self._MODULE_NAME, name='framework_data')

        for channel in self.channels:
            try:
                self._data[channel].extend(data.get_data_on_channel(channel))
            except KeyError:
                raise NonCompatibleData(module=self._MODULE_NAME, name='framework_data')

    def input_2d_data(self, data: List[list]):
        """This method is used to input 2D data into the ``FrameworkData`` object. A 2D data is a
        list of lists. Each list in the list of lists is a channel of data. The data is
        checked to ensure that it is compatible with the data that is already stored in the
        ``FrameworkData`` object. If the data is compatible, then the data is input. If the data
        is not compatible, then an exception is raised.

        :param data: The data that is to be input.
        :type data: List[list]

        :raises NonCompatibleData: Raised when the data that is being input is not compatible with the data that is already stored in the ``FrameworkData`` object.

        :return: None
        """

        if len(data) == 0:
            return

        if len(data[0]) == 0:
            return

        self_data_len = len(self._data)
        input_data_len = len(data)
        if self_data_len == 0:
            raise NonCompatibleData(module=self._MODULE_NAME, name='framework_data')
        if self_data_len != input_data_len:
            raise NonCompatibleData(module=self._MODULE_NAME, name='framework_data')

        for index, channel in enumerate(self._data):
            self.input_data_on_channel(data[index], channel)

    def input_data_on_channel(self, data: list = [], channel: str = None):
        """This method is used to input data onto a specific channel in the ``FrameworkData``
        object.

        :param data: The data that is to be input. Defaults to [].
        :param channel: The channel that the data is to be input on. Defaults to None.
        :type data: list, optional
        :type channel: str, optional

        :return: None
        """

        if len(data) == 0:
            return

        if channel is None:
            if len(self.channels) < 1:
                self.channels.append(self._DEFAULT_CHANNEL_NAME)
            channel = self.channels[0]
        if channel not in self._data:
            self._data[channel] = []

        if channel not in self.channels:
            self.channels.append(channel)
            self._channels_set = None

        self._data[channel].extend(data)

    def get_data_single_channel(self) -> list:
        """This method is used to get the data that is stored on the first channel in the
        ``FrameworkData`` object. Since no channel is specified, the first channel is returned.

        :param None:

        :raises NonCompatibleData: Raised when the data that is being input is not compatible with the data that is already stored in the ``FrameworkData`` object.

        :return: The data that is stored on the first channel in the ``FrameworkData`` object.
        :rtype: list
        """

        if not self.is_1d():
            raise NonCompatibleData(module=self._MODULE_NAME, name='framework_data',
                                    cause='operation_allowed_on_single_channel_only')
        return self.get_data_on_channel(self.channels[0])

    def get_data_on_channel(self, channel: str) -> list:
        """This method is used to get the data that is stored on a specific channel in the
        ``FrameworkData`` object.

        :param channel: The channel that the data is to be retrieved from.
        :type channel: str

        :return: The data that is stored on the specified channel in the ``FrameworkData`` object.
        :rtype: list
        """

        return self._data[channel]

    def get_data(self) -> Dict[str, list]:
        """This method is used to get the all data that is stored in the ``FrameworkData`` object.

        :param None:

        :return: All the data that is stored in the ``FrameworkData`` object.
        :rtype: dict
        """

        return self._data

    def __getitem__(self, item: str) -> List:
        """This method is used to get the data that is stored on a specific channel in the 
        ``FrameworkData`` object. This is a wrapper for the get_data_on_channel class method.

        :param item: The channel that the data is to be retrieved from.
        :type item: str

        :return: The data that is stored on the specified channel in the ``FrameworkData`` object.
        :rtype: list
        """
        return self.get_data_on_channel(item)

    def get_data_as_2d_array(self) -> List[list]:
        """This method is used to get the data that is stored in the ``FrameworkData`` object as a
        2D array. The data is returned as a list of lists. Each list in the list of lists is a
        channel of data.

        :param None:

        :return: The data that is stored in the ``FrameworkData`` object as a 2D array.
        :rtype: List[list]
        """
        return_value = []
        for channel in self.channels:
            return_value.append(self._data[channel])
        return return_value

    def get_data_at_index(self, index: int) -> Dict[str, list]:
        """This method is used to get the data that is stored in the ``FrameworkData`` object at a
        specific index. It basically returns the data at the specified index for each channel in the
        ``FrameworkData`` object. This is used to get the data at a specific time step.

        :param index: The index that you want the data from.
        :type index: int

        :return: The data that is stored in the ``FrameworkData`` object at the specified index.
        :rtype: Dict[str, list]
        """

        return_value = {}
        for channel in self.channels:
            return_value[channel] = self._data[channel][index]
        return return_value

    def has_data(self) -> bool:
        """This method is used to check if the ``FrameworkData`` object has any data stored in it.

        :param None:

        :return: ``True`` if the ``FrameworkData`` object has data stored in it, ``False`` otherwise.
        :rtype: bool
        """

        return len(self._data) > 0 and len(self._data[self.channels[0]]) > 0

    def is_1d(self) -> bool:
        """This method is used to check if the ``FrameworkData`` object has data stored in it on only
        one channel.

        :param None:

        :return: ``True`` if the ``FrameworkData`` object has data stored in it on only one channel, otherwise ``False``.
        :rtype: bool
        """
        return len(self._data) == 1

    def splice(self, start_index: int, count: int) -> FrameworkData:
        """This method is used remove a given number of data points from a starting index and returns the removed items.

        :param start_index: index of removal start
        :param count: number of data points to be removed

        :return: ``FrameworkData`` with all original channels, and removed data.
        :rtype: FrameworkData
        """
        return_value: FrameworkData = FrameworkData(self.sampling_frequency, self.channels)
        end_index = start_index + count
        for channel in self.channels:
            return_value.input_data_on_channel(self._data[channel][start_index:end_index], channel)
            del self._data[channel][start_index:end_index]
        return return_value
