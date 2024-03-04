import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt

# imort the UI file
from UI.Ui_mainWindow import Ui_MainWindow

# main program
if __name__ == "__main__":
      
      # initialize all the necessary objects
      app = QApplication(sys.argv) # create the application
      mainWindow = QMainWindow() # create the main window
      ui = Ui_MainWindow() # create the UI object
      
      # define the ui
      ui.setupUi(mainWindow) # setup the UI

      # show the main window
      mainWindow.show()
      sys.exit(app.exec_())
