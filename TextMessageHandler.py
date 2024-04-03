import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QThread

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
        self.ui.disconnect_btn.clicked.connect(self.__broadcast_message_test)

    def __onUserPressEnterInChat(self):
        # get the message from the UI
        message = self.ui.chat_input.text()
        if message == "":
            return

        # clear the chat input box
        self.ui.chat_input.clear()

        # add the message into the chat box
        self.ui.chatbox.append(f"{self.connectionHandler.client.username}: {message}")

        print(f"Client selected IP is:{self.connectionHandler.client.host_ip}")

        # send the message to the server
        # self.client.send_message(message)

    def __broadcast_message_test(self):
        self.connectionHandler.broadcast_message("Hello World", ChatHeader.TEXT)

