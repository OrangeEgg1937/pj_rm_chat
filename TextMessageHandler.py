import sys
import json
import asyncio
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWebSockets import QWebSocket
from qasync import QEventLoop
import pyttsx3

from UI.Ui_mainWindow import Ui_MainWindow
from connection.host import ChatroomHost
from connection.data_definition import ChatHeader, ChatData
from ConnectionHandler import ConnectionHandler


# define the Text Message Box Handler
class TextMessageHandler:
    def __init__(self, mainWindow: QMainWindow, ui: Ui_MainWindow, connectionHandler: ConnectionHandler):
        # initialize all the necessary objects
        self.mainWindow = mainWindow
        self.ui = ui
        self.connectionHandler = connectionHandler

        # register the signal
        self.ui.chat_input.returnPressed.connect(self.__onUserPressEnterInChat)

        # register the signal
        self.ui.ttsToggle.clicked.connect(self.__ttsToggleClicked)

        # register the header callback
        self.connectionHandler.connect_header_callback(ChatHeader.TEXT, self.__OnNewMessageComing)

        self.ttsActive = False
        self.isReading = False
        self.readList = []

        # start text to speech loop
        asyncio.run_coroutine_threadsafe(self.__shouldIReadText(), self.connectionHandler.event_loop)

    def __onUserPressEnterInChat(self):
        # get the message from the UI
        message = self.ui.chat_input.text()
        if message == "":
            return

        # clear the chat input box
        self.ui.chat_input.clear()

        # check if the client is connected
        if self.connectionHandler.isConnected == 0:
            return

        # build the full message
        message = f"{self.connectionHandler.client.name} ({self.connectionHandler.client.client_id}): {message}"

        # send the message to the server
        self.connectionHandler.send_data(message, ChatHeader.TEXT)

    def __OnNewMessageComing(self, data: ChatData):
        # add the message into the chat box
        message = data.data
        self.ui.chatbox.append(message)
        if (self.ttsActive):
            self.readList.append(message)

    def __ttsToggleClicked(self):
        if not self.ttsActive:
            self.ttsActive = True
        else:
            self.ttsActive = False
            self.readList.clear()

    async def __shouldIReadText(self):
        while True:
            # Checks if there is new message to read
            if (len(self.readList) != 0 and self.isReading == False):
                task = asyncio.create_task(self.__readText())
                await task
            await asyncio.sleep(0.5)

    async def __readText(self):
        self.isReading = True
        message = self.readList.pop()

        # Initialize the converter
        converter = pyttsx3.init()

        # set text to speed properties
        converter.setProperty('rate', 150)
        converter.setProperty('volume', 0.7)

        converter.say(message)
        # Call blocking function with executor
        await self.connectionHandler.event_loop.run_in_executor(None, self.__playText, converter)
        self.isReading = False

    def __playText(self, converter):
        converter.runAndWait()
