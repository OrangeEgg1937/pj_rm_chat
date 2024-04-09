import sys
import json
import asyncio
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWebSockets import QWebSocket
from qasync import QEventLoop

from UI.Ui_mainWindow import Ui_MainWindow
from connection.host import ChatroomHost
from connection.client import ChatroomClient
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

        # register the header callback
        self.connectionHandler.connect_header_callback(ChatHeader.TEXT, self.__OnNewMessageComing)

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
