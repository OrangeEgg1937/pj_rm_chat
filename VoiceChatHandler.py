import io
import sys
import queue
import json
import asyncio
import numpy as np
import zlib
import sounddevice as sd
import threading

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QThread

from UI.Ui_mainWindow import Ui_MainWindow
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
        self.current_pkg = 0
        self.audioBuffer = queue.Queue()

        self._raw_audio_data = None

        # register the signal
        self.ui.push_to_talk.clicked.connect(self.__start_speaking)

        # add the header callback
        self.connectionHandler.connect_header_callback(ChatHeader.AUDIO, self.__audio_data_in)

        # start the output audio thread
        self._audioOut_thread = QThread()
        self._audioOut_thread.run = self.__play_audio_thread
        # self._audioOut_thread.start()

        # start the input audio thread
        self._userSpeakThread = QThread()
        self._userSpeakThread.run = self.__voice_transmit

    # define the voice transmit function
    def __voice_transmit(self):
        self._stream = sd.RawInputStream(channels=1, dtype='int16', samplerate=SAMPLE_RATE, callback=None)
        self._stream.start()
        while True:
            if self.isSpeaking:
                # get the audio buffer
                buffer, overflow = self._stream.read(1024*16)
                raw_audio_data = buffer[:]

                if raw_audio_data is None:
                    continue

                # compress the audio data
                compressed_data = zlib.compress(raw_audio_data)

                # send the audio data to the server
                self.connectionHandler.send_data(compressed_data, ChatHeader.AUDIO)

            else:
                self._stream.stop()
                break

    # define the start speaking function
    def __start_speaking(self):
        # if user is not connected, then return
        if self.connectionHandler.isConnected == 0:
            return

        if self.isSpeaking:
            self.ui.tipsMessage.setText("Push to talk")
            self.isSpeaking = False
        else:
            self.ui.tipsMessage.setText("Now speaking...")
            self.isSpeaking = True
            self._raw_audio_data = b''
            self._userSpeakThread.start()

    # define the callback function for play the audio
    def __audio_data_in(self, message: ChatData):
        pass
        # # decompress the audio data
        # decompressed_data = zlib.decompress(message.data)
        #
        # # convert the audio data to numpy array
        # decompressed_data = np.frombuffer(decompressed_data, dtype=np.int16)

        # adding the decompressed data to the audio buffer
        # self.audioBuffer.put(decompressed_data)

    def __play_audio_thread(self):
        _audioOut = sd.OutputStream(channels=1, dtype='int16', samplerate=SAMPLE_RATE, callback=None)
        _audioOut.start()
        while True:
            if not self.audioBuffer.empty():
                audio_data = self.audioBuffer.get()
                _audioOut.write(audio_data)
            else:
                continue
