import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWebSockets import QWebSocket
from qasync import QEventLoop
import zlib
import numpy as np

from UI.Ui_mainWindow import Ui_MainWindow
from connection.host import ChatroomHost
from connection.client import ChatroomClient
from connection.data_definition import ChatHeader, ChatData
from ConnectionHandler import ConnectionHandler
from connection.host import chatroom


# define the Text Message Box Handler
class VoiceRecordHandler:
    def __init__(self, mainWindow: QMainWindow, ui: Ui_MainWindow, connectionHandler: ConnectionHandler, host):
        # initialize all the necessary objects
        self.mainWindow = mainWindow
        self.ui = ui
        self.host = host
        self.connectionHandler = connectionHandler
        self.audio_buffers = dict()
        self.isRecording = False

        # register the signal
        self.ui.recording_voice.clicked.connect(self.handle_record_audio)
        self.connectionHandler.connect_header_callback(ChatHeader.RECORDING, self.handle_record_audio)
        self.connectionHandler.connect_header_callback(ChatHeader.DONE_RECORDING, self.__onRecordingFinish)

    def __onRecordBtnClick(self):
        # TODO: link button to start/stop recording
        # if not self.audio_buffers:
        #     self.connectionHandler.send_data(None, ChatHeader.RECORDING)
        pass


    async def handle_record_audio(self, data: ChatData):
        if data.header == ChatHeader.RECORDING:
            decompressed_data = zlib.decompress(data.data)

            # Buffer the decompressed data
            if data.senderIP not in self.audio_buffers:
                self.audio_buffers[data.senderIP] = []
            self.audio_buffers[data.senderIP].append(decompressed_data)

    async def __onRecordingFinish(self):
        if self.audio_buffers:
            mixed_audio = self.mix_audio_buffers(self.audio_buffers)

            await chatroom.broadcast_message(mixed_audio, ChatHeader.RECORDING_FILE)

            # Clear the buffers after mixing
            self.audio_buffers.clear()

    def mix_audio_buffers(self, audio_buffers):
        if not audio_buffers:
            return None

        audios = [np.frombuffer(buffer, dtype=np.int16) for buffer in audio_buffers.values()]

        # Mix the audio clips using mean in numpy array
        mixed_audio = np.mean(np.array(audios), axis=0).astype(np.int16).tobytes()

        return mixed_audio