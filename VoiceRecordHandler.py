import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWebSockets import QWebSocket
from qasync import QEventLoop
import zlib
import numpy as np
import wave
import time

from UI.Ui_mainWindow import Ui_MainWindow
from connection.host import ChatroomHost
from connection.data_definition import ChatHeader, ChatData
from ConnectionHandler import ConnectionHandler
from connection.host import ChatroomHost


# define the Text Message Box Handler
class VoiceRecordHandler:
    def __init__(self, mainWindow: QMainWindow, ui: Ui_MainWindow, connectionHandler: ConnectionHandler):
        # initialize all the necessary objects
        self.mainWindow = mainWindow
        self.ui = ui
        self.connectionHandler = connectionHandler
        self.isRecording = False
        self.file_path = "./recorded.wav"

        self._num_channels = 1
        self._bit_per_sample = 16
        self._sample_rate = 44100

        self._recording_start_time = -1  # -1 means not yet started
        self.recording_buffer = []

        # register the signal
        self.ui.recording_voice.clicked.connect(self.__onRecordBtnClick)
        # self.ui.play_recording.clicked.connect(self.__requestRecordingFile)

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

    def generate_wav(self, message: ChatData):
        # ChunkID (RIFF)
        content = 0x52494646.to_bytes(4, 'big')
        # ChunkSize
        content += int(36 + len(message.data)).to_bytes(4, 'little')
        # Format
        content += 0x57415645.to_bytes(4, 'big')

        # Subchunk1ID (fmt-chunk)
        content += 0x666d7420.to_bytes(4, 'big')
        # Subchunk1Size (16 for PCM)
        content += int(16).to_bytes(4, 'little')
        # AudioFormat (PCM)
        content += int(1).to_bytes(2, 'little')
        # NumChannels
        content += int(self._num_channels).to_bytes(2, 'little')
        # SampleRate
        content += int(self._num_channels).to_bytes(4, 'little')
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
        subchunk2Size = len(message.data) + 8
        content += int(subchunk2Size).to_bytes(4, 'little')
        # Data
        content += message.data

        return content

    def write(self, message: ChatData):
        with open(self.file_path, "wb") as file:
            file.write(self.generate_wav(message))
            file.close()

    # process of the received audio data
    def onReceivedAudio(self, decompressed_data: bytes):
        padding_time = 0
        if not self.isRecording:
            return
        if self._starting_time == -1:
            self._starting_time = time.time()
        else:
            padding_time = time.time() - self._starting_time
            self._starting_time = time.time()

        # check whether the audio need to be padded if the padding time is more than 1 second
        if padding_time > 1:
            # padding the zero audio raw data bytes according to the padding time
            padding_size = int(padding_time * self.sample_rate * self.num_channels * self.bits_per_sample / 8)
            padding_data = np.zeros(padding_size, dtype=np.int16).tobytes()
            self.recording_buffer.append(padding_data)

        # add the audio data to the buffer
        self.recording_buffer.append(decompressed_data)

    # client start recording the incoming audio
    def __onRecordStart(self):
        self.isRecording = True
        self.ui.recording_tips.setText("You are recording")

    def __onRecordFinish(self):
        self.isRecording = False
        self.ui.recording_tips.setText("Recording end~")
        self.__generate_wav()
        self._starting_time = -1

    # processing the recording file to wav file
    def __generate_wav(self):
        # set the file path and name of the recorded audio
        self.file_path = f"./recorded_{int(time.time())}_{self.connectionHandler.client.name}_.wav"

        # calculate the total size of the audio data
        total_size = 0
        for data in self.recording_buffer:
            total_size += len(data)

        # ChunkID (RIFF)
        content = 0x52494646.to_bytes(4, 'big')
        # ChunkSize
        content += int(36 + total_size).to_bytes(4, 'little')
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
        subchunk2Size = total_size + 8
        content += int(subchunk2Size).to_bytes(4, 'little')
        # Data
        for data in self.recording_buffer:
            content += data

        # save the audio data to the file
        with open(self.file_path, "wb") as file:
            file.write(content)
            file.close()

    def __transfer_recording(self):
        if self.isRecording:
            return
        self.connectionHandler.send_data('', ChatHeader.RECORDING_FILE)
