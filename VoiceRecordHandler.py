import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWebSockets import QWebSocket
from qasync import QEventLoop
import zlib
import numpy as np
import wave
import time
import os
import base64

from UI.Ui_mainWindow import Ui_MainWindow
from connection.data_definition import ChatHeader, ChatData
from ConnectionHandler import ConnectionHandler

# define the sample rate
SAMPLE_RATE = 44100


class RecordingFragments:
    def __init__(self, raw_bytes):
        self.raw_bytes = raw_bytes
        self.received_time = time.time()

    def extract_with_start_end_time(self, start_time, end_time):
        # padding the 0 bytes if the start time earlier than the recorded time
        if abs(start_time - self.received_time) > 0.1:  # padding if the time difference is more than 0.1 second
            padding_size = abs(int((self.received_time - start_time) * SAMPLE_RATE))
            padding_data = np.zeros(padding_size, dtype=np.int16).tobytes()
            self.raw_bytes = padding_data + self.raw_bytes

        # padding the 0 bytes if the end time later than the recorded time
        if abs(end_time - self.received_time) > 0.1:  # padding if the time difference is more than 0.1 second
            padding_size = abs(int((end_time - self.received_time) * SAMPLE_RATE))
            padding_data = np.zeros(padding_size, dtype=np.int16).tobytes()
            self.raw_bytes = self.raw_bytes + padding_data

        return self.raw_bytes


# define the Text Message Box Handler
class VoiceRecordHandler:
    def __init__(self, mainWindow: QMainWindow, ui: Ui_MainWindow, connectionHandler: ConnectionHandler):
        # initialize all the necessary objects
        self.mainWindow = mainWindow
        self.ui = ui
        self.connectionHandler = connectionHandler
        self.isRecording = False
        self.file_path = "./recorded.wav"
        self.downloading_file_name = ""

        self._num_channels = 1
        self._bit_per_sample = 16
        self._sample_rate = 44100

        self._recording_start_time = -1  # -1 means not yet started
        self._recording_end_time = -1  # -1 means not yet started
        self.recording_buffer = []

        # register the signal
        self.ui.recording_voice.clicked.connect(self.__onRecordBtnClick)
        self.ui.play_recording.clicked.connect(self.__onUserClickPlayRecording)

        # register the header callback
        self.connectionHandler.connect_header_callback(ChatHeader.RECORDING_FILE, self.__onRecordingFileListReceived)
        self.connectionHandler.connect_header_callback(ChatHeader.REQUEST_RECORDING_FILE, self.__onRecordingFileReceived)

    @property
    def num_channels(self):
        return self._num_channels

    @property
    def sample_rate(self):
        return self._sample_rate

    @property
    def bits_per_sample(self):
        return self._bit_per_sample

    @property
    def bytes_rate(self):
        return self.sample_rate * self.num_channels * self.bits_per_sample / 8

    @property
    def block_align(self):
        return self.num_channels * self.bits_per_sample / 8

    def __onRecordBtnClick(self):
        if not self.isRecording:
            self.isRecording = True
            print("Recording started")
            self.__onRecordStart()
        else:
            self.isRecording = False
            print("Recording finished")
            self.__onRecordFinish()

    # process of the received audio data
    def onReceivedAudio(self, decompressed_data: bytes):
        padding_time = 0
        if not self.isRecording:
            return

        fragment = RecordingFragments(decompressed_data)
        self.recording_buffer.append(fragment)

    # client start recording the incoming audio
    def __onRecordStart(self):
        self.isRecording = True
        self._recording_start_time = time.time()
        self.ui.recording_tips.setText("You are recording")

    def __onRecordFinish(self):
        self.isRecording = False
        self._recording_end_time = time.time()
        self.ui.recording_tips.setText("Recording end~")
        raw_bytes_audio = self.__combine_audio()
        self.__generate_wav(raw_bytes_audio)
        self.__transfer_recording()
        self._recording_start_time = -1
        self._recording_end_time = -1

    # combine the buffer into one audio file
    def __combine_audio(self):
        # getting all audio data into a new list
        audio_data = []
        for fragment in self.recording_buffer:
            audio_data.append(
                fragment.extract_with_start_end_time(self._recording_start_time, self._recording_end_time))

        numpyBuffer = [np.frombuffer(buffer, dtype=np.int16) for buffer in audio_data]

        # Find the length of the longest fragment
        max_length = max(len(fragment) for fragment in numpyBuffer)

        # Pad all fragments to the length of the longest fragment
        padded_fragments = [np.pad(fragment, (0, max_length - len(fragment))) for fragment in numpyBuffer]

        # mix the audio clips using mean in numpy array
        result = np.mean(padded_fragments, axis=0).astype(np.int16).tobytes()

        return result

    # processing the recording file to wav file
    def __generate_wav(self, raw_data: bytes):
        # set the file path and name of the recorded audio
        self.file_path = f"./recorded_{int(time.time())}_{self.connectionHandler.client.name}_.wav"

        # ChunkID (RIFF)
        content = 0x52494646.to_bytes(4, 'big')
        # ChunkSize
        content += int(36 + len(raw_data)).to_bytes(4, 'little')
        # Format
        content += 0x57415645.to_bytes(4, 'big')

        # Subchunk1ID (fmt-chunk)
        content += 0x666d7420.to_bytes(4, 'big')
        # Subchunk1Size (16 for PCM)
        content += int(16).to_bytes(4, 'little')
        # AudioFormat (PCM)
        content += int(1).to_bytes(2, 'little')
        # NumChannels
        content += int(self.num_channels).to_bytes(2, 'little')
        # SampleRate
        content += int(self.sample_rate).to_bytes(4, 'little')
        # ByteRate
        content += int(self.bytes_rate).to_bytes(4, 'little')
        # BlockAlign
        content += int(self.block_align).to_bytes(2, 'little')
        # BitsPerSample
        content += int(self.bits_per_sample).to_bytes(2, 'little')

        # Subchunk2ID (data-chunk)
        content += 0x64617461.to_bytes(4, 'big')
        # Subchunk2Size
        # Subchunk2Size == size of "data" subchunk = Subchunk2ID + subchunk2Size + raw data in bytes
        subchunk2Size = len(raw_data) + 8
        content += int(subchunk2Size).to_bytes(4, 'little')
        # Data
        content += raw_data

        # save the audio data to the file
        with open(self.file_path, "wb") as file:
            file.write(content)
            file.close()

    def __transfer_recording(self):
        if self.file_path == "":
            return
        with open(self.file_path, "rb") as file:
            filename = self.file_path.split("/")[-1]
            self.connectionHandler.send_data(filename, ChatHeader.RECORDING_FILE_NAME)
            data = file.read()
            # compress the data
            data = zlib.compress(data)
            self.connectionHandler.send_data(data, ChatHeader.RECORDING_FILE)

    def __onRecordingFileListReceived(self, message: ChatData):
        # clear the current list
        self.ui.recording_list.clear()

        file_list = json.loads(message.data)

        for file in file_list:
            item = QListWidgetItem(file)
            self.ui.recording_list.addItem(item)

    def __onUserClickPlayRecording(self):
        # get the selected item
        item = self.ui.recording_list.currentItem()
        if item is None:
            return

        # get the file name
        file_name = item.text()

        # construct the full path of the file
        file_path = os.path.join("./record_download", file_name)

        # check if the file exists
        if os.path.exists(file_path):
            print("Playing the recording...")
        else:
            self.downloading_file_name = file_name
            self.ui.play_recording.setEnabled(False)
            self.ui.recording_tips.setText("Downloading the file...Please wait")
            self.connectionHandler.send_data(file_name, ChatHeader.REQUEST_RECORDING_FILE)

    def __onRecordingFileReceived(self, data: ChatData):
        # get the file name
        raw_data = data.data

        # convert back to bytes from base64
        raw_data = base64.b64decode(raw_data)

        # decompress the data
        raw_data = zlib.decompress(raw_data)

        # construct the full path of the file
        file_path = os.path.join("./record_download", self.downloading_file_name)

        # save the file
        with open(file_path, "wb") as file:
            file.write(raw_data)
            file.close()

        self.ui.play_recording.setEnabled(True)
        self.ui.recording_tips.setText("File downloaded successfully, you can select and play the file now")
