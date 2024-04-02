import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt

from UI.Ui_mainWindow import Ui_MainWindow
from connection.host import ChatroomHost
from connection.client import ChatroomClient


# define the Text Message Box Handler
class TextMessageHandler:
    def __init__(self, mainWindow: QMainWindow, ui: Ui_MainWindow, client: ChatroomClient):
        # initialize all the necessary objects
        self.mainWindow = mainWindow
        self.ui = ui
        self.client = client

        # register the signal
        self.ui.chat_input.returnPressed.connect(self.__onUserPressEnterInChat)

    def __onUserPressEnterInChat(self):
        # get the message from the UI
        message = self.ui.chat_input.text()
        if message == "":
            return

        # clear the chat input box
        self.ui.chat_input.clear()

        # add the message into the chat box
        self.ui.chatbox.append(f"{self.client.username}: {message}")

        print(f"Client selected IP is:{self.client.host_ip}")

        # send the message to the server
        # self.client.send_message(message)
