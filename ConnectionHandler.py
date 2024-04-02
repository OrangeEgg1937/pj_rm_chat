import sys
import threading
import asyncio

from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QListWidget
from PyQt5.QtCore import Qt, QThread

from UI.Ui_mainWindow import Ui_MainWindow
from connection.host import ChatroomHost
from connection.client import ChatroomClient
from connection.data_definition import ChatHeader, ChatData
from websockets.sync.client import connect as ws_connect


class ConnectionHandler:
    def __init__(self, mainWindow: QMainWindow, ui: Ui_MainWindow, client: ChatroomClient):
        # initialize all the necessary objects
        self.mainWindow = mainWindow
        self.ui = ui
        self.connection_type = 0  # 0: no yet connect, 1: host, 2: client
        self.client = client
        self.host = None

        # register the signal
        self.ui.connectBtn.clicked.connect(self.__onConnectButtonClicked)
        self.ui.connectToLocalhost.clicked.connect(lambda: self.__onConnectButtonClicked(1))

        self.ui.hostBtn.clicked.connect(self.__onHostButtonClicked)
        self.ui.hostLocalhost.clicked.connect(lambda: self.__onHostButtonClicked(1))

        self.ui.connect_to_chat.clicked.connect(self.__onConnectToChatButtonClicked)

    # connect button clicked
    def __onConnectButtonClicked(self, method: int = 0):
        # check the user option type
        if method == 0:
            threading.Thread(self.__search_host(f"ws://{self.ui.target_ip.text()}:60000")).start()
        else:
            threading.Thread(self.__search_host("ws://localhost:60000")).start()

    def __onHostButtonClicked(self, method: int = 0):
        # get the host ip
        ip = self.ui.target_ip.text()
        # get the port information
        port = int(self.ui.chatroom_port.text())

        # disable other button and input information
        self.setConnectionPlaneEnabled(False)

        self.connection_type = 1

        # check the user option type
        if method == 0:
            # create a host object
            self.host = (ChatroomHost(ip, self.ui.username.text(), port))
            self.__host_chatroom()
        else:
            # create a host object
            self.host = (ChatroomHost("localhost", self.ui.username.text(), port))
            self.__host_chatroom()

    def __onConnectToChatButtonClicked(self):
        # get the selected item from the list
        selected_item = self.ui.chatroom_list.currentItem().data(Qt.UserRole)

        # if the selected item is None or unknown object, then return
        if selected_item is None or not isinstance(selected_item, dict):
            return

        # print the selected item
        print(f"Selected item: {selected_item}\n IP address: {selected_item}")

        # set destination
        destination = selected_item["senderIP"]
        # try to connect to the host
        try:
            # init a connection to the host
            self.client.connect_to_host(destination)
            # disable the connection plane
            self.setConnectionPlaneEnabled(False)
            # set the success message
            self.ui.StatusMsg.setText(f"{selected_item["name"]}")
            self.ui.connectionMsg.setText(f"Connected!")
            # set the connection type
            self.connection_type = 2
        except Exception as e:
            # set the error message
            self.ui.StatusMsg.setText("Connection failed, try another one")
            self.ui.connectionMsg.setText(f"Failed")
            print(f"Error: {e}")

    # search the host
    def __search_host(self, destination: str):
        # update the client object
        self.client.host_ip = destination

        # request the host list
        self.client.request_host_list()

        # update the UI
        self.ui.chatroom_list.clear()
        for host in self.client.hostList:
            # Create QListWidgetItem and set the name
            item = QListWidgetItem(self.client.hostList[host]["name"])
            item.setData(Qt.UserRole, self.client.hostList[host])

            # Add the item to the list
            self.ui.chatroom_list.addItem(item)

    def __host_chatroom(self):
        # update the UI
        self.ui.chatroom_list.clear()
        self.ui.StatusMsg.setText("You are hosting a chatroom now!")
        self.ui.connectionMsg.setText(f"Hosting")

        # run the host server
        self.thread = QThread()
        self.thread.run = (lambda: asyncio.run(self.host.start()))
        self.thread.start()

    def setConnectionPlaneEnabled(self, available: bool):
        self.ui.username.setEnabled(available)
        self.ui.target_ip.setEnabled(available)
        self.ui.chatroom_name.setEnabled(available)
        self.ui.chatroom_port.setEnabled(available)
        self.ui.hostBtn.setEnabled(available)
        self.ui.hostLocalhost.setEnabled(available)
        self.ui.connectBtn.setEnabled(available)
        self.ui.connectToLocalhost.setEnabled(available)
        self.ui.connect_to_chat.setEnabled(available)

