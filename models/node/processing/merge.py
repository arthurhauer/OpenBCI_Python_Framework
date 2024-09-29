import abc
import string
from random import choices
from typing import List, Dict, Final
from models.framework_data import FrameworkData
from models.node.processing.synchronize import Synchronize


# {
# "nodes": {
#     "root": {
#         "node_a": {
#             ...,
#             "output": {
#                 "data_a": [
#                     {"node": "merge",
#                     "input": "master_main"}
#                 ],
#                 "timestamp": [
#                     {"node": "merge",
#                     "input": "master_timestamp"}
#                 ]
#             },
#         },
#         "node_b": {
#             ...,
#             "output": {
#                 "data_b": [
#                     {
#                         "node": "merge",
#                         "input": "slave_main"
#                     }
#                 ],
#                 "timestamp": [
#                     {"node": "merge",
#                     "input": "slave_timestamp"}
#                 ]
#             },
#         }
#     },
#     "common": {
#         "merge": {
#             "module": "models.node.processing",
#             "type": "Merge",
#             ...
#         }
#     },
#     ...
# }
#     }


class Merge(Synchronize):
    """ This node merges the data from the master and the slave. The master data is always kept. If the slave data
    contains a channel that is also present in the master data, the slave data is renamed to a new channel name and
    added to the master data. This node also automatically synchronizes the data if the slave data is not synchronized
    with the master data.
    This node usage is a bit tricky. It goes in the "common" section of the configuration file, and it needs to have
    at least two nodes before him (the master and the slave) that will point their outputs to this "merge" node. Those 
    previous nodes must have a additional "timestamp" property, that will define if they have a master or a slave timestamp.
    The "output" property of this previous node will also have a property that defines if this node will be the master or
    the slave. Here's an example of the previous nodes "output" and "timestamp" properties:

    .. code-block:: 

        {
            "nodes": {
                "root": {
                    "node_a": {
                        ...,
                        "output": {
                            "data_a": [
                                {
                                    "node": "merge",
                                    "input": "master_main"
                                }
                            ],
                            "timestamp": [
                                {
                                    "node": "merge",
                                    "input": "master_timestamp"
                                    }
                            ]
                        },
                    }, 
                    "node_b": {
                        ...,
                        "output": {
                            "data_b": [
                                {
                                    "node": "merge",
                                    "input": "slave_main"
                                }
                            ],
                            "timestamp": [
                                {
                                    "node": "merge",
                                    "input": "slave_timestamp"
                                }
                            ]
                        },
                    }
                },
                "common": {
                    "merge": {
                        "module": "models.node.processing",
                        "type": "Merge",
                        ...
                    }
                },
                ...
            }
        }

    ``configuration.json`` usage:
        **module** (*str*): Current module name (in this case ``models.node.processing``).\n
        **type** (*str*): Current node type (in this case ``Merge``).\n
        **slave_filling** (*str*): Slave filling type. It can be ``zero_fill`` or ``sample_and_hold``.\n
        **statistics_enabled** (*bool*): If ``True``, the node will calculate the synchronization error statistics.\n
        **buffer_options** (*dict*): Buffer options:
            **clear_output_buffer_on_data_input** (*bool*): If ``True``, the output buffer will be cleared when data is inputted.\n
            **clear_input_buffer_after_process** (*bool*): If ``True``, the input buffer will be cleared after the node is executed.\n
            **clear_output_buffer_after_process** (*bool*): If ``True``, the output buffer will be cleared after the node is executed.\n
    """
    _MODULE_NAME: Final[str] = 'node.processing.merge'

    OUTPUT_MERGED_MAIN: Final[str] = 'merged_main'
    OUTPUT_MERGED_TIMESTAMP: Final[str] = 'merged_timestamp'

    @abc.abstractmethod
    def _validate_parameters(self, parameters: dict):
        """Validates the parameters that were passed to the node. In this case it just calls the parent method.
        """
        super()._validate_parameters(parameters)

    @abc.abstractmethod
    def _initialize_parameter_fields(self, parameters: dict):
        """Initializes the parameters that were passed to the node. In this case it just calls the parent method.
        """
        super()._initialize_parameter_fields(parameters)

    def _is_next_node_call_enabled(self) -> bool:
        """ This method allows the next node call. In this case it enables whenever there's data in the output buffer.
        """
        return self._output_buffer[self.OUTPUT_MERGED_MAIN].get_data_count() > 0

    def _process(self, data: Dict[str, FrameworkData]) -> Dict[str, FrameworkData]:
        """ This method processes the data that was inputted to the node. It merges the master and the slave data.
        
        :param data: The data that was inputted to the node.
        :type data: Dict[str, FrameworkData]

        :return: The merged data.
        :rtype: Dict[str, FrameworkData]
        """
        synchronized_data: Dict[str, FrameworkData] = super()._process(data)
        new_slave_data = synchronized_data[self.OUTPUT_SYNCHRONIZED_SLAVE]
        master_main = synchronized_data[self.OUTPUT_SYNCHRONIZED_MASTER]
        merged_data = FrameworkData()
        merged_data.extend(master_main)
        for channel in new_slave_data.channels:
            new_channel_name = channel
            if channel in merged_data.channels:
                rand_id = ''.join(choices(string.ascii_uppercase + string.digits, k=10))
                new_channel_name = f'{channel}{rand_id}'
            merged_data.input_data_on_channel(new_slave_data.get_data_on_channel(channel), new_channel_name)

        return {
            self.OUTPUT_MERGED_MAIN: merged_data,
            self.OUTPUT_MERGED_TIMESTAMP: synchronized_data[self.OUTPUT_SYNCHRONIZED_TIMESTAMP]
        }

    def _get_outputs(self) -> List[str]:
        """ This method returns the outputs of the node. In this case it returns the merged data and the merged timestamp.
        """
        return [
            self.OUTPUT_MERGED_MAIN,
            self.OUTPUT_MERGED_TIMESTAMP
        ]
