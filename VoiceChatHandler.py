import io
import sys
import json
import asyncio
import numpy
import zlib
import sounddevice as sd
import threading

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QThread
from qasync import QEventLoop

from UI.Ui_mainWindow import Ui_MainWindow
from connection.host import ChatroomHost
from connection.client import ChatroomClient
from connection.data_definition import ChatHeader, ChatData
from ConnectionHandler import ConnectionHandler

# define the sample rate
SAMPLE_RATE = 44100


# define the Voice chat function class
class VoiceChatHandler:
    def __init__(self, mainWindow: QMainWindow, ui: Ui_MainWindow, connectionHandler: ConnectionHandler):
        # initialize all the necessary objects
        self.mainWindow = mainWindow
        self.ui = ui
        self.connectionHandler = connectionHandler
        self.isSpeaking = False

        self._raw_audio_data = None
        self._stream = sd.RawInputStream(channels=1, callback=self.__voice_transmit, dtype='int16')

        # register the signal
        self.ui.push_to_talk.clicked.connect(self.__start_speaking)

        # add the header callback
        self.connectionHandler.connect_header_callback(ChatHeader.AUDIO, self.__play_audio)

    # define the voice transmit function
    def __voice_transmit(self, indata, frames, time, status):
        self._raw_audio_data += bytes(indata)
        if len(self._raw_audio_data) > 1024 * 1024:
            # compress the audio data
            compressed_data = zlib.compress(self._raw_audio_data)
            print(f"Compressed: {len(compressed_data)}")

            # transmit the audio data
            self.connectionHandler.send_data(compressed_data, ChatHeader.AUDIO)

            # reset the raw audio data buffer
            self._raw_audio_data = b''

    # define the start speaking function
    def __start_speaking(self):
        # if user is not connected, then return
        if self.connectionHandler.connection_type == 0:
            return

        if self.isSpeaking:
            self.ui.tipsMessage.setText("Push to talk")
            self.isSpeaking = False
            self._stream.stop()
        else:
            self.ui.tipsMessage.setText("Now speaking...")
            self.isSpeaking = True
            self._raw_audio_data = b''
            self._stream.start()

    # define the callback function for play the audio
    def __play_audio(self, message: ChatData):
        # decompress the audio data
        decompressed_data = zlib.decompress(message.data)
        print(f"Decompressed: {len(decompressed_data)}")
        print(f"Decompressed: {decompressed_data}")
        print(f"====================")

        # convert the audio data to numpy array
        decompressed_data = numpy.frombuffer(decompressed_data, dtype=numpy.int16)

        # starting a new thread to play the audio
        threading.Thread(target=self.__play_audio_thread, args=(decompressed_data,)).start()

    def __play_audio_thread(self, audio_data: numpy.ndarray):
        # play the audio
        sd.play(audio_data, samplerate=SAMPLE_RATE, device=sd.default.device)
        sd.wait()