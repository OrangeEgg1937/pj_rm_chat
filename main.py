import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt

# import the UI file
from UI.Ui_mainWindow import Ui_MainWindow
from ConnectionHandler import ConnectionHandler

# main program
if __name__ == "__main__":
    # initialize all the necessary objects
    app = QApplication(sys.argv)  # create the application
    mainWindow = QMainWindow()  # create the main window
    ui = Ui_MainWindow()  # create the UI object

    # define the ui
    ui.setupUi(mainWindow)  # set up the UI

    # import the UI logic related class
    connectionHandler = ConnectionHandler(mainWindow, ui)

    # show the main window
    mainWindow.show()
    sys.exit(app.exec_())
