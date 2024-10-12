from models.framework_data import FrameworkData
from models.node.generator.generator_node import GeneratorNode


class SingleRunGeneratorNode(GeneratorNode):
    """This node generates data for a single run. It is used to get the data from a non real-time source, such as a
    CSV file, and feed it to the framework. It is not meant to be used in a real-time scenario, as it is not
    thread-safe. It is meant to be used in a single run scenario, such as a batch processing scenario.

    This node is not meant to be used directly, but to be inherited by other nodes that implement the
    ``_generate_data`` method. This method is responsible for generating the data for a single run. The node will
    generate the data for all the trials in the run, and then stop executing.

    :param parameters: The parameters of the node(default: None).
    :type parameters: dict
    """

    def __init__(self, parameters=None):
        self._first_execution = True
        super().__init__(parameters)

    def run(self, data: FrameworkData = None, input_name: str = None) -> None:
        """This method runs the node. It is called by the framework when the node is executed. If this is the first
        execution, it will run. If it is not the first execution, it will raise an exception.

        :param data: The data that will be passed to the node. This comes from the previous node in the pipeline(default: None).
        :type data: FrameworkData
        :param input_name: The name of the input that the data comes from(default: None).
        :type input_name: str

        :raises Exception: If this is not the first execution.
        """
        if self._first_execution:
            super().run()
            self._first_execution = False
