from threading import Thread
from typing import List

import numpy
import time
from brainflow import BrainFlowInputParams, BoardShim, BoardIds, LogLevels
from nptyping import Float
from numpy.typing import NDArray

import models.data.processing.feature_extraction.dummy
from config.configuration import Configuration
from models.data.processing.classification.classification import Classification
from models.data.processing.classification.classifier import Classifier
from models.data.processing.feature_extraction.feature_extraction import FeatureExtraction
from models.data.processing.feature_extraction.feature_extractor import FeatureExtractor
from models.data.processing.preprocessing.preprocessing import PreProcessing
from models.session.session import Session


class OpenBCIBoard:

    def __init__(self,
                 communication: dict,
                 preprocessing: PreProcessing = None,
                 feature_extractor: FeatureExtractor = models.data.processing.feature_extraction.dummy.Dummy(),
                 classifier: Classifier = models.data.processing.classification.dummy.Dummy(),
                 session: Session = None,
                 log_level: str = "OFF",
                 board: str = "SYNTHETIC_BOARD"
                 ) -> None:
        super().__init__()
        self._board = None
        self._timestamp_channel = None
        self._eeg_channels = None
        self._eeg_channel_names = None
        self._accelerometer_channels = None
        self._marker_channel = None
        self._set_log_level(log_level=log_level)
        self._set_brain_flow_input_parameters(communication)
        self._get_board(board=board)
        self._sampling_rate = None
        self.get_sampling_rate()
        self.get_eeg_channels()
        self.get_accelerometer_channels()
        self.get_timestamp_channel()
        self.get_marker_channel()
        self._run_stream_loop: bool = False
        self._data_loop_thread = Thread(target=self._stream_data_loop, daemon=True)
        self._data_callback = None
        self.preprocessing = preprocessing
        self.session = session
        self.feature_extractor = feature_extractor
        self._feature_extractor_train = True
        self.classifier = classifier
        self._classifier_train = True
        self._data = None
        self._inserting_marker = False
        self._markers_to_insert = []

    @classmethod
    def from_config_json(cls):
        board = cls(
            log_level=Configuration.get_open_bci_log_level(),
            board=Configuration.get_open_bci_board(),
            communication=Configuration.get_open_bci_communication(),
            session=Session.from_config_json(Configuration.get_trial_settings())
        )
        board.preprocessing = PreProcessing.from_config_json(Configuration.get_preprocessing_settings())
        board.feature_extractor = FeatureExtraction.from_config_json(Configuration.get_feature_extraction_settings())
        board.classifier = Classification.from_config_json(Configuration.get_classification_settings())
        board.session.on_stop = board.close_session
        board.session.on_feature_extractor_training_end = board._stop_training_feature_extractor
        board.session.on_classifier_training_end = board._stop_training_classifier
        board.session.on_change_trial = board.insert_marker
        return board

    @staticmethod
    def _set_log_level(log_level: str = "OFF"):
        if log_level is None:
            log_level = "OFF"
        log_level = "LEVEL_" + log_level
        BoardShim.set_log_level(LogLevels[log_level])

    @staticmethod
    def _get_board_type(board: str = "SYNTHETIC_BOARD") -> int:
        return BoardIds[board]

    def _set_brain_flow_input_parameters(self, parameters: dict):
        self._brain_flow_parameters = BrainFlowInputParams()
        if 'ip-port' in parameters:
            self._brain_flow_parameters.ip_port = parameters['ip-port']
        if 'mac-address' in parameters:
            self._brain_flow_parameters.mac_address = parameters['mac-address']
        if 'other-info' in parameters:
            self._brain_flow_parameters.other_info = parameters['other-info']
        if 'serial-number' in parameters:
            self._brain_flow_parameters.serial_number = parameters['serial-number']
        if 'ip-address' in parameters:
            self._brain_flow_parameters.ip_address = parameters['ip-address']
        if 'ip-protocol' in parameters:
            self._brain_flow_parameters.ip_protocol = parameters['ip-protocol']
        if 'timeout' in parameters:
            self._brain_flow_parameters.ip_protocol = parameters['timeout']
        if 'file' in parameters:
            self._brain_flow_parameters.file = parameters['file']
        if 'serial-port' in parameters:
            self._brain_flow_parameters.serial_port = parameters['serial-port']

    def _get_brain_flow_input_parameters(self):
        return self._brain_flow_parameters

    def _get_board(self, board: str = "SYNTHETIC_BOARD") -> BoardShim:
        if self._board is None:
            self._board = BoardShim(self._get_board_type(board=board), self._get_brain_flow_input_parameters())
        return self._board

    def get_sampling_rate(self) -> int:
        if self._sampling_rate is None:
            self._sampling_rate = BoardShim.get_sampling_rate(self._get_board().board_id)
            Configuration.set_sampling_frequency(self._sampling_rate)
        return self._sampling_rate

    def get_eeg_channel_names(self) -> List[str]:
        if self._eeg_channel_names is None:
            self._eeg_channel_names = BoardShim.get_eeg_names(self._get_board().board_id)
        return self._eeg_channel_names

    def get_timestamp_channel(self) -> int:
        if self._timestamp_channel is None:
            self._timestamp_channel = BoardShim.get_timestamp_channel(self._get_board().board_id)
        return self._timestamp_channel

    def get_eeg_channels(self) -> List[int]:
        if self._eeg_channels is None:
            self._eeg_channels = BoardShim.get_eeg_channels(self._get_board().board_id)
        return self._eeg_channels

    def get_marker_channel(self) -> int:
        if self._marker_channel is None:
            self._marker_channel = BoardShim.get_marker_channel(self._get_board().board_id)
        return self._marker_channel

    def get_accelerometer_channels(self) -> List[int]:
        if self._accelerometer_channels is None:
            self._accelerometer_channels = BoardShim.get_accel_channels(self._get_board().board_id)
        return self._accelerometer_channels

    def open_session(self):
        self._get_board().prepare_session()

    def start_stream(self):
        if not self._get_board().is_prepared():
            self.open_session()
        self._get_board().start_stream()
        time.sleep(2)

    def _get_marker_data(self):
        markers_to_remove = []
        marker_channel_index = len(self.get_eeg_channels())
        timestamp_channel_index = marker_channel_index + 2
        sampling_rate_s = 1 / self.get_sampling_rate()
        current_data_len = len(self._data[timestamp_channel_index])
        for index, (timestamp, code) in enumerate(self._markers_to_insert):
            filtered = list(
                filter(lambda element: timestamp - sampling_rate_s >= element <= timestamp + sampling_rate_s,
                       self._data[timestamp_channel_index][current_data_len - 100:current_data_len - 1]))
            len_filtered = len(filtered)
            if len_filtered > 0:
                closest_point = min(range(len(filtered)), key=lambda i: abs(filtered[i] - timestamp))
                marker_index = numpy.where(self._data[timestamp_channel_index] == filtered[closest_point])[0][0]
                self._data[marker_channel_index][marker_index] = code
                markers_to_remove.append((timestamp, code))
        for (timestamp, code) in markers_to_remove:
            self._markers_to_insert.remove((timestamp, code))

    def get_data(self) -> NDArray[Float]:
        data = self._get_board().get_board_data()
        eeg_data = data[self.get_eeg_channels()]
        timestamp_data = data[self.get_timestamp_channel()]
        marker_data = numpy.zeros(len(timestamp_data))

        accelerometer_data = data[self.get_accelerometer_channels()]

        self.preprocessing.process(eeg_data)

        data = numpy.vstack([eeg_data, marker_data, timestamp_data, accelerometer_data])

        if self._data is None:
            self._data = data
        else:
            self._data = numpy.append(self._data, data, axis=1)

        self._get_marker_data()

        self._feature_extractor_process(data)

        self._classifier_process(data)

        return self._data

    def _feature_extractor_process(self, data):
        if self._feature_extractor_train:
            pass
        else:
            self.feature_extractor.process(data,len(self.get_eeg_channels()))

    def _classifier_process(self, data):
        if self._classifier_train:
            pass
        else:
            self.classifier.process(data,len(self.get_eeg_channels()))

    def _stop_training_feature_extractor(self):
        print("Starting feature extractor training")
        self.feature_extractor.train(self._data, len(self.get_eeg_channels()))
        self._feature_extractor_train = False
        self._classifier_train = True
        print("Finished feature extractor training")

    def _stop_training_classifier(self):
        print("Starting classifier training")
        self.classifier.train(self._data, len(self.get_eeg_channels()))
        self._classifier_train = False
        print("Finished feature extractor training")

    def insert_marker(self, code: int):
        self._inserting_marker = True
        self._markers_to_insert.append((time.time(), code))
        self._inserting_marker = False

    def _stream_data_loop(self):
        self.session.start()
        while self._run_stream_loop:
            if self._inserting_marker:
                time.sleep(0.05)
            else:
                time.sleep(Configuration.get_open_bci_data_callback_frequency_ms() / 1000)
                self._data_callback(self.get_data())

    def start_data_loop(self):
        self._run_stream_loop = True
        self.start_stream()
        self._data_loop_thread.start()

    def set_data_callback(self, on_data_callback):
        self._data_callback = on_data_callback

    def start_stream_callback(self, on_data_callback):
        self.set_data_callback(on_data_callback)
        self.start_data_loop()

    def close_session(self):
        self._run_stream_loop = False
        self._data_loop_thread.join()
        self._get_board().stop_stream()
        self._get_board().release_session()
