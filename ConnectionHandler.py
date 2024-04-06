import sys
import threading
import asyncio
import json

from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QListWidget
from PyQt5.QtCore import Qt, QThread

from UI.Ui_mainWindow import Ui_MainWindow
from connection.host import ChatroomHost
from connection.client import ChatroomClient
from connection.data_definition import ChatHeader, ChatData
from qasync import QEventLoop


class ConnectionHandler:
    def __init__(self, mainWindow: QMainWindow, ui: Ui_MainWindow, client: ChatroomClient, event_loop: QEventLoop, host: ChatroomHost = None):
        # initialize all the necessary objects
        self.mainWindow = mainWindow
        self.ui = ui
        self.connection_type = 0  # 0: no yet connect, 1: host, 2: client
        self.client = client
        self.host = host
        self.event_loop = event_loop
        self.__header_callback_pool = None

        # register the signal
        self.ui.connectBtn.clicked.connect(self.__onConnectButtonClicked)
        self.ui.connectToLocalhost.clicked.connect(lambda: self.__onConnectButtonClicked(1))

        self.ui.hostBtn.clicked.connect(self.__onHostButtonClicked)
        self.ui.hostLocalhost.clicked.connect(lambda: self.__onHostButtonClicked(1))

        self.ui.connect_to_chat.clicked.connect(self.__onConnectToChatButtonClicked)

        self.ui.disconnect_btn.clicked.connect(self.disconnect)

        # init the header_callback_pool
        self.connect_header_callback(ChatHeader.CHATROOM_LIST, self.update_member_list)

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

        try:
            # disable other button and input information
            self.setConnectionPlaneEnabled(False)
            self.connection_type = 1

            # check the user option type
            if method == 0:
                # create a host object
                self.host = (ChatroomHost(ip, self.ui.chatroom_name.text(), port))
                # copy the callback to the connection
                self.__copy_callback_into_connection()
                self.event_loop.create_task(self.__host_chatroom())
            else:
                # create a host object
                self.host = (ChatroomHost("localhost", self.ui.chatroom_name.text(), port))
                # copy the callback to the connection
                self.__copy_callback_into_connection()
                self.event_loop.create_task(self.__host_chatroom())
        except Exception as e:
            print(f"Error: {e}")
            self.ui.StatusMsg.setText("See console for more information")
            self.ui.connectionMsg.setText(f"Failed")

    def __onConnectToChatButtonClicked(self):
        # get the selected item from the list
        selected_item = self.ui.chatroom_list.currentItem().data(Qt.UserRole)

        # if the selected item is None or unknown object, then return
        if selected_item is None or not isinstance(selected_item, dict):
            return

        # print the selected item
        print(f"Selected item-IP address: {selected_item["senderIP"]}")

        # update the user information
        self.client.username = self.ui.username.text()

        # set destination
        destination = selected_item["senderIP"]
        # try to connect to the host
        try:
            # set the connection type
            self.connection_type = 2
            # copy the callback to the connection
            self.__copy_callback_into_connection()
            # init a connection to the host
            self.thread = QThread()
            self.thread.run = (lambda: self.client.connect_to_host(destination))
            self.thread.start()
            # disable the connection plane
            self.setConnectionPlaneEnabled(False)
            while self.client.connectionID is None:
                print("Waiting for a ID")
            # set the success message
            self.ui.StatusMsg.setText(f"{selected_item["name"]}, Your ID:{self.client.connectionID}")
            self.ui.connectionMsg.setText(f"Connected!")
        except Exception as e:
            # set the error message
            self.ui.StatusMsg.setText("See console for more information")
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

    async def __host_chatroom(self):
        try:
            # update the UI
            self.ui.chatroom_list.clear()
            self.ui.StatusMsg.setText("Hosting...")
            self.ui.connectionMsg.setText(f"Waiting...")

            # set the host info
            self.host.host_info.name = self.ui.username.text()

            # start the host
            task = self.event_loop.create_task(self.host.start())

            while not self.host.isHosted:
                exception = task.done()
                if exception:
                    error = task.exception()
                    raise Exception("Failed to host the chatroom")
                print("Waiting for the host to start...")
                await asyncio.sleep(1)

            # set the success message
            self.ui.StatusMsg.setText(f"You hosted at {self.host.host_name}")
            self.ui.connectionMsg.setText(f"Connected")

            # update the client object
            self.client.host_ip = f"ws://{self.host.host_ip}:{self.host.port}"
            self.client.username = self.ui.username.text()
            self.client.connectionID = 0

            # add the host to the chatroom list
            item = QListWidgetItem(f"{self.client.username}_{self.client.connectionID}")
            item.setData(Qt.UserRole, self.host)
            self.ui.memberlist.addItem(item)

            # set the connection type
            self.connection_type = 1

            # loop the event
            while True:
                exception = task.done()
                if exception:
                    error = task.exception()
                    raise Exception("Failed during host the chatroom")
                await asyncio.sleep(1)

        except Exception as e:
            # clean up the connection when it is failed
            print(f"Error: {e}\nReason:{error}\nTips:Have you run the Chatroom server?")
            self.ui.StatusMsg.setText("See console for more information")
            self.ui.connectionMsg.setText(f"Failed/Disconnected")
            # enable the connection plane
            self.setConnectionPlaneEnabled(True)
            # reset the connection information
            self.connection_type = 0

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

    # define a public method for broadcasting message
    def broadcast_message(self, message: str, header: ChatHeader):
        # check the connection type
        if self.connection_type != 1:
            print("You are not the host")
            return
        self.event_loop.create_task(self.host.broadcast_message(message, header))

    # update the member list
    def update_member_list(self, data: ChatData):
        # update the UI
        self.ui.memberlist.clear()
        # get the package data
        member_list = data.data
        # convert json string to dict
        chat_member = json.loads(member_list)
        print(chat_member)
        for member in chat_member:
            print(member)
            name = f"{chat_member[member]["name"]} ({chat_member[member]["client_id"]})"
            # Create QListWidgetItem and set the name
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, chat_member[member])

            # Add the item to the list
            self.ui.memberlist.addItem(item)

    # client disconnect
    def disconnect(self):
        if self.connection_type == 1:
            return
        self.event_loop.create_task(self.client.disconnect())

    # init the header callback pool
    def __init_header_callback_pool(self):
        self.__header_callback_pool = dict()
        for header in ChatHeader:
            self.__header_callback_pool[header] = []

    # add the function to the header callback poll
    def connect_header_callback(self, header: ChatHeader, callback):
        if self.__header_callback_pool is None:
            self.__init_header_callback_pool()
        if header not in self.__header_callback_pool:
            raise ValueError(f"Header {header} is not in the header list")
        self.__header_callback_pool[header].append(callback)

    # copy the pool to the header callback
    def __copy_callback_into_connection(self):
        if self.__header_callback_pool is None:
            return
        # check the connection type
        if self.connection_type == 2:
            for header in self.__header_callback_pool:
                for callback in self.__header_callback_pool[header]:
                    self.client.connect_header_callback(header, callback)
        elif self.connection_type == 1:
            for header in self.__header_callback_pool:
                for callback in self.__header_callback_pool[header]:
                    self.host.connect_header_callback(header, callback)

    # send the message to the server
    def send_data(self, data, header: ChatHeader):
        if self.connection_type == 1:
            self.broadcast_message(data, header)
        elif self.connection_type == 2:
            self.client.send_data(data, header, self.event_loop)
