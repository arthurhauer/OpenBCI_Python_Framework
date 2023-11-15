import copy
import csv
import os
from threading import Thread
from typing import List, Final, Dict

import sys
import time
from pyqtgraph import GraphicsWindow
from pyqtgraph.Qt import QtGui
from PyQt5 import QtWidgets

from models.exception.invalid_parameter_value import InvalidParameterValue
from models.exception.missing_parameter import MissingParameterError
from models.framework_data import FrameworkData
from models.node.output.output_node import OutputNode


class SimpleGraph(OutputNode):
    """ This node displays it's input in the console.
    "plot_signal": {
         "module": "models.node.output.display",
         "type": "SimpleGraph",
         "window": 500,
         "buffer_options": {
         },
         "outputs": {
         }
     }
    Attributes:
        _MODULE_NAME (str): The name of this module (in this case, 'node.output.display').
        INPUT_MAIN (str): The name of the main input (in this case, 'main').
    
    ``configuration.json`` usage example:

        **name**: Current node instance name (in this case, ``plot_signal``).\n
        **type**: Node type (in this case ``SimpleGraph``).\n
        **module**: Current module name (in this case ``models.node.output.display``).\n
        **window**: Plotting window size, in samples (in this case, 500 samples).\n

    """

    _MODULE_NAME: Final[str] = 'node.output.file.simplegraph'

    INPUT_MAIN: Final[str] = 'main'

    def _validate_parameters(self, parameters: dict):
        """ Validates the parameters that were passed to the node.

        :param parameters: The parameters that were passed to the node.
        :type parameters: dict

        """
        super()._validate_parameters(parameters)
        if 'window' not in parameters:
            raise MissingParameterError(
                module=self._MODULE_NAME, name=self.name,
                parameter='window'
            )
        if type(parameters['window']) is not int:
            raise InvalidParameterValue(module=self._MODULE_NAME, name=self.name,
                                        parameter='window',
                                        cause='must_be_int')

    def _initialize_parameter_fields(self, parameters: dict):
        """ Initializes the parameters that were passed to the node.

        :param parameters: The parameters that were passed to the node.
        :type parameters: dict
        """
        super()._initialize_parameter_fields(parameters)
        self.window = parameters['window']
        self.app = QtGui.QApplication([])
        self.win = GraphicsWindow(title=self.name, size=(800, 600))
        self.data_buffer = FrameworkData()
        self.curves = {}

    def _get_inputs(self) -> List[str]:
        """ Returns the input names of this node.
        """
        return [
            self.INPUT_MAIN
        ]

    def _is_processing_condition_satisfied(self) -> bool:
        return self._input_buffer[self.INPUT_MAIN].get_data_count() > 0

    def _init_plots_curves(self, input_data: FrameworkData) -> None:
        for index, channel in enumerate(input_data.channels):
            plot = self.win.addPlot(row=index, col=0)
            plot.showAxis('left', False)
            plot.setMenuEnabled('left', False)
            plot.showAxis('bottom', False)
            plot.setMenuEnabled('bottom', False)
            plot.setTitle(channel)
            self.curves[channel] = plot.plot()

    def _plot_data(self, input_data: FrameworkData) -> None:
        for channel in input_data.channels:
            self.curves[channel].setData(input_data.get_data_on_channel(channel))
        self.app.processEvents()


    def _process(self, data: Dict[str, FrameworkData]) -> None:
        """ Runs the node.
        """
        input_data = data[self.INPUT_MAIN]
        self.data_buffer = input_data.splice(0, self.window)
        if len(self.curves) == 0:
            self._init_plots_curves(self.data_buffer)
        self._plot_data(self.data_buffer)

    def dispose(self) -> None:
        """ Node self implementation of disposal of allocated resources.
        """
        self._clear_output_buffer()
        self._clear_input_buffer()
        del self.curves
        self.app.quit()
        super().dispose()
