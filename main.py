import sys
import asyncio
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QThread

# import the UI file
from UI.Ui_mainWindow import Ui_MainWindow
from ConnectionHandler import ConnectionHandler
from TextMessageHandler import TextMessageHandler
from VoiceChatHandler import VoiceChatHandler
from VoiceRecordHandler import VoiceRecordHandler
from KaraokeHandler import KaraokeHandler
from qasync import QEventLoop

# main program
if __name__ == "__main__":
    # initialize all the necessary objects
    app = QApplication(sys.argv)  # create the application
    mainWindow = QMainWindow()  # create the main window
    ui = Ui_MainWindow()  # create the UI object

    # define the event loop
    event_loop = QEventLoop(app)
    asyncio.set_event_loop(event_loop)

    # define the ui
    ui.setupUi(mainWindow)  # set up the UI

    """
    Adding your function below this line
    
    For creating a new class, please at least add the following parameters:
    mainWindow: QMainWindow                 <= For the main window
    ui: Ui_MainWindow                       <= For UI object
    connectionHandler: ConnectionHandler    <= For all connection related function
    
    P.S: if want to add async function, please use connectionHandler.event_loop.create_task(async_function())
    """

    # import the UI logic related class (Please add the function here)
    connectionHandler = ConnectionHandler(app=app, mainWindow=mainWindow, ui=ui, event_loop=event_loop)
    TextMessageHandler = TextMessageHandler(mainWindow, ui, connectionHandler)
    VoiceRecordHandler = VoiceRecordHandler(mainWindow, ui, connectionHandler)
    KaraokeHandler = KaraokeHandler(mainWindow, ui, connectionHandler)
    voiceChatHandler = VoiceChatHandler(mainWindow, ui, connectionHandler, VoiceRecordHandler)


    """
    Do not modify the code below
    """

    # define app close event
    app_close_event = asyncio.Event()

    # disconnect the application when user exit
    app.aboutToQuit.connect(app_close_event.set)

    # show the main window
    mainWindow.show()

    with event_loop:
        event_loop.run_forever()
