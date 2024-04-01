# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'E:\CSCI3280\project\onlineChatroom\UI\mainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1065, 747)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalFrame = QtWidgets.QFrame(self.centralwidget)
        self.verticalFrame.setStyleSheet("QFrame{\n"
"     border: 1px solid rgb(0, 0, 0)\n"
" }")
        self.verticalFrame.setObjectName("verticalFrame")
        self.userAndChatroomLayout = QtWidgets.QVBoxLayout(self.verticalFrame)
        self.userAndChatroomLayout.setObjectName("userAndChatroomLayout")
        self.userIcon = QtWidgets.QPushButton(self.verticalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.userIcon.sizePolicy().hasHeightForWidth())
        self.userIcon.setSizePolicy(sizePolicy)
        self.userIcon.setMinimumSize(QtCore.QSize(100, 100))
        self.userIcon.setMaximumSize(QtCore.QSize(100, 100))
        self.userIcon.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon/man.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.userIcon.setIcon(icon)
        self.userIcon.setIconSize(QtCore.QSize(60, 60))
        self.userIcon.setAutoRepeat(False)
        self.userIcon.setAutoExclusive(False)
        self.userIcon.setObjectName("userIcon")
        self.userAndChatroomLayout.addWidget(self.userIcon)
        self.NameTag = QtWidgets.QLabel(self.verticalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.NameTag.sizePolicy().hasHeightForWidth())
        self.NameTag.setSizePolicy(sizePolicy)
        self.NameTag.setMinimumSize(QtCore.QSize(0, 0))
        self.NameTag.setStyleSheet("Border :none")
        self.NameTag.setObjectName("NameTag")
        self.userAndChatroomLayout.addWidget(self.NameTag)
        self.Username = QtWidgets.QLineEdit(self.verticalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Username.sizePolicy().hasHeightForWidth())
        self.Username.setSizePolicy(sizePolicy)
        self.Username.setMinimumSize(QtCore.QSize(130, 0))
        self.Username.setMaximumSize(QtCore.QSize(130, 16777215))
        self.Username.setObjectName("Username")
        self.userAndChatroomLayout.addWidget(self.Username)
        self.IPTag_2 = QtWidgets.QLabel(self.verticalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.IPTag_2.sizePolicy().hasHeightForWidth())
        self.IPTag_2.setSizePolicy(sizePolicy)
        self.IPTag_2.setMinimumSize(QtCore.QSize(0, 0))
        self.IPTag_2.setStyleSheet("Border:none")
        self.IPTag_2.setObjectName("IPTag_2")
        self.userAndChatroomLayout.addWidget(self.IPTag_2)
        self.IPaddress_2 = QtWidgets.QLineEdit(self.verticalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.IPaddress_2.sizePolicy().hasHeightForWidth())
        self.IPaddress_2.setSizePolicy(sizePolicy)
        self.IPaddress_2.setMinimumSize(QtCore.QSize(130, 0))
        self.IPaddress_2.setMaximumSize(QtCore.QSize(100, 16777215))
        self.IPaddress_2.setObjectName("IPaddress_2")
        self.userAndChatroomLayout.addWidget(self.IPaddress_2)
        self.IPTag = QtWidgets.QLabel(self.verticalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.IPTag.sizePolicy().hasHeightForWidth())
        self.IPTag.setSizePolicy(sizePolicy)
        self.IPTag.setMinimumSize(QtCore.QSize(0, 0))
        self.IPTag.setMaximumSize(QtCore.QSize(130, 16777215))
        self.IPTag.setStyleSheet("Border:none")
        self.IPTag.setObjectName("IPTag")
        self.userAndChatroomLayout.addWidget(self.IPTag)
        self.IPaddress = QtWidgets.QLineEdit(self.verticalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.IPaddress.sizePolicy().hasHeightForWidth())
        self.IPaddress.setSizePolicy(sizePolicy)
        self.IPaddress.setMinimumSize(QtCore.QSize(130, 0))
        self.IPaddress.setMaximumSize(QtCore.QSize(130, 16777215))
        self.IPaddress.setObjectName("IPaddress")
        self.userAndChatroomLayout.addWidget(self.IPaddress)
        self.hostBtn = QtWidgets.QPushButton(self.verticalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.hostBtn.sizePolicy().hasHeightForWidth())
        self.hostBtn.setSizePolicy(sizePolicy)
        self.hostBtn.setMinimumSize(QtCore.QSize(130, 0))
        self.hostBtn.setObjectName("hostBtn")
        self.userAndChatroomLayout.addWidget(self.hostBtn)
        self.hostLocalhost = QtWidgets.QPushButton(self.verticalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.hostLocalhost.sizePolicy().hasHeightForWidth())
        self.hostLocalhost.setSizePolicy(sizePolicy)
        self.hostLocalhost.setMinimumSize(QtCore.QSize(130, 0))
        self.hostLocalhost.setObjectName("hostLocalhost")
        self.userAndChatroomLayout.addWidget(self.hostLocalhost)
        self.connectBtn = QtWidgets.QPushButton(self.verticalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.connectBtn.sizePolicy().hasHeightForWidth())
        self.connectBtn.setSizePolicy(sizePolicy)
        self.connectBtn.setMinimumSize(QtCore.QSize(130, 0))
        self.connectBtn.setObjectName("connectBtn")
        self.userAndChatroomLayout.addWidget(self.connectBtn)
        self.connectToLocalhost = QtWidgets.QPushButton(self.verticalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.connectToLocalhost.sizePolicy().hasHeightForWidth())
        self.connectToLocalhost.setSizePolicy(sizePolicy)
        self.connectToLocalhost.setMinimumSize(QtCore.QSize(130, 0))
        self.connectToLocalhost.setObjectName("connectToLocalhost")
        self.userAndChatroomLayout.addWidget(self.connectToLocalhost)
        self.label_4 = QtWidgets.QLabel(self.verticalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setMinimumSize(QtCore.QSize(130, 0))
        self.label_4.setStyleSheet("Border:none")
        self.label_4.setObjectName("label_4")
        self.userAndChatroomLayout.addWidget(self.label_4)
        self.listView = QtWidgets.QListView(self.verticalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listView.sizePolicy().hasHeightForWidth())
        self.listView.setSizePolicy(sizePolicy)
        self.listView.setMinimumSize(QtCore.QSize(0, 200))
        self.listView.setMaximumSize(QtCore.QSize(130, 16777215))
        self.listView.setObjectName("listView")
        self.userAndChatroomLayout.addWidget(self.listView)
        self.connectBtn_2 = QtWidgets.QPushButton(self.verticalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.connectBtn_2.sizePolicy().hasHeightForWidth())
        self.connectBtn_2.setSizePolicy(sizePolicy)
        self.connectBtn_2.setMaximumSize(QtCore.QSize(130, 16777215))
        self.connectBtn_2.setObjectName("connectBtn_2")
        self.userAndChatroomLayout.addWidget(self.connectBtn_2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.userAndChatroomLayout.addItem(spacerItem)
        self.gridLayout.addWidget(self.verticalFrame, 1, 0, 1, 1)
        self.statusLayout = QtWidgets.QHBoxLayout()
        self.statusLayout.setObjectName("statusLayout")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setObjectName("label_6")
        self.statusLayout.addWidget(self.label_6)
        self.connectionMsg = QtWidgets.QLabel(self.centralwidget)
        self.connectionMsg.setObjectName("connectionMsg")
        self.statusLayout.addWidget(self.connectionMsg)
        self.gridLayout.addLayout(self.statusLayout, 0, 0, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setObjectName("listWidget")
        item = QtWidgets.QListWidgetItem()
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icon/girl.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(icon1)
        self.listWidget.addItem(item)
        self.verticalLayout.addWidget(self.listWidget)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout_3.addWidget(self.textBrowser)
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout_3.addWidget(self.lineEdit)
        self.verticalLayout.addLayout(self.verticalLayout_3)
        self.gridLayout.addLayout(self.verticalLayout, 1, 3, 1, 1)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setMaximumSize(QtCore.QSize(16777215, 10))
        self.label_3.setObjectName("label_3")
        self.verticalLayout_4.addWidget(self.label_3)
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setMinimumSize(QtCore.QSize(0, 200))
        self.widget.setStyleSheet("background:black")
        self.widget.setObjectName("widget")
        self.verticalLayout_4.addWidget(self.widget)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/chatroom/numute.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.pushButton_2.setIcon(icon2)
        self.pushButton_2.setIconSize(QtCore.QSize(50, 50))
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_3.addWidget(self.pushButton_2)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout_5.addWidget(self.checkBox)
        self.keySequenceEdit = QtWidgets.QKeySequenceEdit(self.centralwidget)
        self.keySequenceEdit.setObjectName("keySequenceEdit")
        self.verticalLayout_5.addWidget(self.keySequenceEdit)
        self.horizontalLayout_3.addLayout(self.verticalLayout_5)
        self.pushButton_5 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_5.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/chatroom/webcam.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.pushButton_5.setIcon(icon3)
        self.pushButton_5.setIconSize(QtCore.QSize(50, 50))
        self.pushButton_5.setObjectName("pushButton_5")
        self.horizontalLayout_3.addWidget(self.pushButton_5)
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/chatroom/recording.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.pushButton_3.setIcon(icon4)
        self.pushButton_3.setIconSize(QtCore.QSize(50, 50))
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout_3.addWidget(self.pushButton_3)
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/chatroom/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.pushButton_4.setIcon(icon5)
        self.pushButton_4.setIconSize(QtCore.QSize(50, 50))
        self.pushButton_4.setObjectName("pushButton_4")
        self.horizontalLayout_3.addWidget(self.pushButton_4)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem1)
        self.gridLayout.addLayout(self.verticalLayout_4, 1, 4, 1, 1)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_6.addWidget(self.label_5)
        self.ExtensionTag = QtWidgets.QTabWidget(self.centralwidget)
        self.ExtensionTag.setMinimumSize(QtCore.QSize(0, 400))
        self.ExtensionTag.setStyleSheet("background-color:rgb(255, 255, 255)")
        self.ExtensionTag.setObjectName("ExtensionTag")
        self.voice = QtWidgets.QWidget()
        self.voice.setObjectName("voice")
        self.ExtensionTag.addTab(self.voice, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.ExtensionTag.addTab(self.tab_2, "")
        self.verticalLayout_6.addWidget(self.ExtensionTag)
        self.gridLayout.addLayout(self.verticalLayout_6, 1, 5, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)
        self.label_7.setMinimumSize(QtCore.QSize(30, 0))
        self.label_7.setMaximumSize(QtCore.QSize(30, 16777215))
        self.label_7.setObjectName("label_7")
        self.horizontalLayout.addWidget(self.label_7)
        self.StatusMsg = QtWidgets.QLabel(self.centralwidget)
        self.StatusMsg.setObjectName("StatusMsg")
        self.horizontalLayout.addWidget(self.StatusMsg)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 3, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1065, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.ExtensionTag.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "G12 Chatroom"))
        self.NameTag.setText(_translate("MainWindow", "Name"))
        self.IPTag_2.setText(_translate("MainWindow", "Chatroom name:"))
        self.IPTag.setText(_translate("MainWindow", "IP"))
        self.hostBtn.setText(_translate("MainWindow", "Host"))
        self.hostLocalhost.setText(_translate("MainWindow", "Host as localhost"))
        self.connectBtn.setText(_translate("MainWindow", "Connect"))
        self.connectToLocalhost.setText(_translate("MainWindow", "Connect to localhost"))
        self.label_4.setText(_translate("MainWindow", "Chatroom List"))
        self.connectBtn_2.setText(_translate("MainWindow", "Connect to chatroom"))
        self.label_6.setText(_translate("MainWindow", "Connection:"))
        self.connectionMsg.setText(_translate("MainWindow", "[No connection]"))
        self.label_2.setText(_translate("MainWindow", "Member"))
        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        item = self.listWidget.item(0)
        item.setText(_translate("MainWindow", "Jack"))
        self.listWidget.setSortingEnabled(__sortingEnabled)
        self.label.setText(_translate("MainWindow", "Chat"))
        self.label_3.setText(_translate("MainWindow", "Video"))
        self.checkBox.setText(_translate("MainWindow", "Push-to-talk"))
        self.label_5.setText(_translate("MainWindow", "Extension"))
        self.ExtensionTag.setTabText(self.ExtensionTag.indexOf(self.voice), _translate("MainWindow", "Karaoke"))
        self.ExtensionTag.setTabText(self.ExtensionTag.indexOf(self.tab_2), _translate("MainWindow", "VC Change"))
        self.label_7.setText(_translate("MainWindow", "Status:"))
        self.StatusMsg.setText(_translate("MainWindow", "N/A"))
import UI.icon_rc


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
