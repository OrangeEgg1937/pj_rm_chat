import io
import sys
import queue
import json
import asyncio
import numpy as np
import zlib
import sounddevice as sd
import threading
import time
import pytz
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtNetwork import QAbstractSocket
from PyQt5.QtCore import Qt, QThread

from UI.Ui_mainWindow import Ui_MainWindow
from connection.data_definition import ChatHeader, ChatData
from ConnectionHandler import ConnectionHandler

# define the sample rate
SAMPLE_RATE = 44100


class AudioPlayer:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.audioBuffer = queue.Queue()
        self._audioOut = sd.OutputStream(channels=1, dtype='int16', samplerate=self.sample_rate, callback=None)
        self._audioOut.start()  # Start the OutputStream once
        self._audio_player_thread = threading.Thread(target=self.play_audio_from_buffer)
        self._audio_player_thread.start()

    def play_audio_from_buffer(self):
        while True:
            if not self.audioBuffer.empty():
                # get the audio data from the buffer
                audio = self.audioBuffer.get()

                # play the audio
                self._audioOut.write(audio)  # Write to the OutputStream continuously
            else:
                # if there is no audio data, wait for a short period of time
                time.sleep(0.1)


# define the Voice chat function class
class VoiceChatHandler:
    def __init__(self, mainWindow: QMainWindow, ui: Ui_MainWindow, connectionHandler: ConnectionHandler):
        # initialize all the necessary objects
        self.mainWindow = mainWindow
        self.ui = ui
        self.connectionHandler = connectionHandler
        self.isSpeaking = False
        self.current_pkg = 0
        self.single_audio_data = b''
        self.audioBuffer = queue.Queue()

        self._raw_audio_data = None

        # register the signal
        self.ui.push_to_talk.clicked.connect(self.__start_speaking)

        # add the header callback
        self.connectionHandler.connect_header_callback(ChatHeader.AUDIO, self.__audio_data_in)

        # build the output audio stream
        self._audioOut = sd.OutputStream(channels=1, dtype='int16', samplerate=SAMPLE_RATE, callback=None)

        # build the input audio stream
        self._stream = sd.RawInputStream(channels=1, dtype='int16', samplerate=SAMPLE_RATE,
                                         callback=self.__voice_transmit)

        # start the audio player thread
        self._audio_player = AudioPlayer(sample_rate=SAMPLE_RATE)

    # define the voice transmit function
    def __voice_transmit(self, indata, frames, time, status):
        # get the audio buffer
        self.single_audio_data += bytes(indata)

        if len(self.single_audio_data) >= SAMPLE_RATE * 2:
            # push the audio data to the buffer
            temp = self.single_audio_data
            # compress the audio data
            compressed_data = zlib.compress(temp)
            currentDateAndTime = datetime.now(pytz.utc)
            print("Compressed size: ", len(compressed_data), "Current Time", currentDateAndTime)
            # send the audio data to the server
            self.connectionHandler.send_data(compressed_data, ChatHeader.AUDIO)
            # clear the audio data
            self.single_audio_data = b''
            # flush the socket
            self.connectionHandler.qtWebSocket.flush()

    # define the start speaking function
    def __start_speaking(self):
        # if user is not connected, then return
        if self.connectionHandler.isConnected == 0:
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

    def __audio_data_in(self, message: ChatData):
        # decompress the audio data
        # current time
        print("Decompressing the audio data...", len(message.data))
        decompressed_data = zlib.decompress(message.data)

        audio = np.frombuffer(decompressed_data, dtype=np.int16)

        currentDateAndTime = datetime.now(pytz.utc)
        print("Received audio data at ", currentDateAndTime)
        # add the audio data to the buffer
        self._audio_player.audioBuffer.put(audio)
