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
import wave

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtNetwork import QAbstractSocket
from PyQt5.QtCore import Qt, QThread

from UI.Ui_mainWindow import Ui_MainWindow
from connection.data_definition import ChatHeader, ChatData
from ConnectionHandler import ConnectionHandler
from VoiceRecordHandler import VoiceRecordHandler, RecordingFragments

# define the sample rate
SAMPLE_RATE = 44100
swidth = 2


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
    def __init__(self, mainWindow: QMainWindow, ui: Ui_MainWindow, connectionHandler: ConnectionHandler, voiceRecordHandler: VoiceRecordHandler):
        # initialize all the necessary objects
        self.mainWindow = mainWindow
        self.ui = ui
        self.connectionHandler = connectionHandler
        self.isSpeaking = False
        self.current_pkg = 0
        self.single_audio_data = b''
        self.audioBuffer = queue.Queue()
        self.recordHandler = voiceRecordHandler

        self._raw_audio_data = None
        self.changePitch = False
        self.pitchStrength = 0

        # register the signal
        self.ui.push_to_talk.clicked.connect(self.__start_speaking)

        # register events to functions
        self.ui.pitchToggle.clicked.connect(self.__onTogglePitch)
        self.ui.PitchSlider.sliderMoved.connect(self.__updateSlider)

        # add the header callback
        self.connectionHandler.connect_header_callback(ChatHeader.AUDIO, self.__audio_data_in)

        # build the output audio stream
        self._audioOut = sd.OutputStream(channels=1, dtype='int16', samplerate=SAMPLE_RATE, callback=None)

        # build the input audio stream
        self._stream = sd.RawInputStream(channels=1, dtype='int16', samplerate=SAMPLE_RATE,
                                         callback=self.__voice_transmit)

        # start the audio player thread
        self._current_audio_player = 0
        self._audio_player0 = AudioPlayer(sample_rate=SAMPLE_RATE)
        self._audio_player1 = AudioPlayer(sample_rate=SAMPLE_RATE)

    # define the voice transmit function
    def __voice_transmit(self, indata, frames, time, status):
        # get the audio buffer
        self.single_audio_data += bytes(indata)

        if len(self.single_audio_data) >= SAMPLE_RATE * 2:
            # push the audio data to the buffer
            temp = self.single_audio_data
            # Apply pitch change if wanted
            if (self.changePitch):
                temp = self.__changePitch(temp)
            # compress the audio data
            compressed_data = zlib.compress(temp)
            currentDateAndTime = datetime.now(pytz.utc)
            print("Compressed size: ", len(compressed_data), "Current Time", currentDateAndTime)
            # send the audio data to the server
            self.connectionHandler.send_data(compressed_data, ChatHeader.AUDIO)
            # if the user is recording, then pass the audio data to record handler for recording
            if self.recordHandler.isRecording:
                fragment = RecordingFragments(temp)
                self.recordHandler.recording_buffer.append(fragment)
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
            self.single_audio_data = b''
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

        # if the user is recording, then pass the audio data to record handler for recording
        if self.recordHandler.isRecording:
            self.recordHandler.onReceivedAudio(decompressed_data)

        audio = np.frombuffer(decompressed_data, dtype=np.int16)

        currentDateAndTime = datetime.now(pytz.utc)
        print("Received audio data at ", currentDateAndTime)
        # add the audio data to the buffer
        if self._current_audio_player == 0:
            self._audio_player0.audioBuffer.put(audio)
            self._current_audio_player = 1
        elif self._current_audio_player == 1:
            self._audio_player1.audioBuffer.put(audio)
            self._current_audio_player = 0

    # Toggles between pitch and no pitch change
    def __onTogglePitch(self):
        if not self.changePitch:
            self.changePitch = True
        else:
            self.changePitch = False

    # Updates slider
    def __updateSlider(self):
        newValue = self.ui.PitchSlider.value()

        self.ui.pitchValue.setText("Pitch: " + str(newValue))
        self.pitchStrength = 2 * newValue

    # Pitch changer
    def __changePitch(self, audio_data):
        audio_data = np.array(wave.struct.unpack("%dh" % (len(audio_data) / swidth), audio_data))

        # do Fourier Transform
        audio_data = np.fft.rfft(audio_data)

        # Pitch shifting
        audio_data2 = [0] * len(audio_data)
        if self.pitchStrength >= 0:
            audio_data2[self.pitchStrength:len(audio_data)] = audio_data[0:(len(audio_data) - self.pitchStrength)]
            audio_data2[0:self.pitchStrength] = audio_data[(len(audio_data) - self.pitchStrength):len(audio_data)]
        else:
            audio_data2[0:(len(audio_data) + self.pitchStrength)] = audio_data[-self.pitchStrength:len(audio_data)]
            audio_data2[(len(audio_data) + self.pitchStrength):len(audio_data)] = audio_data[0:-self.pitchStrength]

        shifted_data = np.array(audio_data2)
        # Done shifting

        # Inverse transform
        shifted_data = np.fft.irfft(shifted_data)

        # Turn data back into buffer like object
        dataout = shifted_data.astype(np.int16).tobytes()

        return dataout
