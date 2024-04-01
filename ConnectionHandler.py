import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt

from UI.Ui_mainWindow import Ui_MainWindow
from connection.host import ChatroomHost


class ConnectionHandler:
    def __init__(self, mainWindow: QMainWindow, ui: Ui_MainWindow):
        # initialize all the necessary objects
        self.mainWindow = mainWindow
        self.ui = ui
        self.connected = False
