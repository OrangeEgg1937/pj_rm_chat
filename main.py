import sys
import asyncio
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt

# import the UI file
from UI.Ui_mainWindow import Ui_MainWindow
from ConnectionHandler import ConnectionHandler
from TextMessageHandler import TextMessageHandler
from connection import client

# main program
if __name__ == "__main__":
    # initialize all the necessary objects
    app = QApplication(sys.argv)  # create the application
    mainWindow = QMainWindow()  # create the main window
    ui = Ui_MainWindow()  # create the UI object

    # define the ui
    ui.setupUi(mainWindow)  # set up the UI

    # define the cline side object
    client = client.ChatroomClient("localhost", port=60000)

    # import the UI logic related class
    connectionHandler = ConnectionHandler(mainWindow, ui, client)
    TextMessageHandler = TextMessageHandler(mainWindow, ui, client)

    # show the main window
    mainWindow.show()
    sys.exit(app.exec_())
