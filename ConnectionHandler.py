import sys
import time
import threading
import asyncio
import json
import subprocess

from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QListWidget
from PyQt5.QtCore import Qt, QThread

from UI.Ui_mainWindow import Ui_MainWindow
from connection.host import ChatroomHost
from connection.client import ChatroomClient
from connection.data_definition import ChatHeader, ChatData
from qasync import QEventLoop


class ConnectionHandler:
    def __init__(self, mainWindow: QMainWindow, ui: Ui_MainWindow, client: ChatroomClient, event_loop: QEventLoop,
                 host: ChatroomHost = None):
        # initialize all the necessary objects
        self.mainWindow = mainWindow
        self.ui = ui
        self.connection_type = 0  # 0: no yet connect, 1: connected
        self.client = client
        self.host = host
        self.event_loop = event_loop
        self.__header_callback_pool = None

        # register the signal
        self.ui.connectBtn.clicked.connect(self.__onConnectButtonClicked)
        self.ui.connectToLocalhost.clicked.connect(lambda: self.__onConnectButtonClicked(1))

        self.ui.hostBtn.clicked.connect(self.__onHostButtonClicked)
        self.ui.hostLocalhost.clicked.connect(lambda: self.__onHostButtonClicked("localhost"))

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

    # for late connection
    async def __connection_late(self):
        await asyncio.sleep(3)
        self.connection_type = 2

    def __onHostButtonClicked(self, ip_address: str = None):
        # if the ip address is None, get the ip address from the input
        if ip_address is None:
            ip_address = self.ui.target_ip.text()

        port = self.ui.chatroom_port.text()
        chatroom_name = self.ui.chatroom_name.text()

        try:
            # disable other button and input information
            self.setConnectionPlaneEnabled(False)
            self.connection_type = 1

            # run the host chatroom in a subprocess
            subThread = QThread()
            subThread.run = (lambda:
                             subprocess.run(["python", "connection/host.py",
                                             "-ip", ip_address,
                                             "-name", chatroom_name,
                                             "-port", f"{port}"],
                                            check=True))
            subThread.start()

            self.event_loop.create_task(self.__connection_late())

            self.ui.StatusMsg.setText("Please wait...")
            self.ui.connectionMsg.setText(f"Connecting...")

            while self.connection_type == 0:
                pass

            # connect to the host
            destination = f"{ip_address}:{port}"
            self.__connect_to_host(destination, chatroom_name)

        except Exception as e:
            print(f"Error: {e}")
            self.ui.StatusMsg.setText("See console for more information")
            self.ui.connectionMsg.setText(f"Failed")
            self.connection_type = 0

    def __onConnectToChatButtonClicked(self):
        # get the selected item from the list
        selected_item = self.ui.chatroom_list.currentItem().data(Qt.UserRole)

        # if the selected item is None or unknown object, then return
        if selected_item is None or not isinstance(selected_item, dict):
            return

        # print the selected item
        print(f"Selected item-IP address: {selected_item['senderIP']}")

        # set destination
        destination = selected_item['senderIP']

        # connect to the host
        self.__connect_to_host(destination, selected_item['name'])

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
            item = QListWidgetItem(self.client.hostList[host]['name'])
            item.setData(Qt.UserRole, self.client.hostList[host])

            # Add the item to the list
            self.ui.chatroom_list.addItem(item)

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
            name = f"{chat_member[member]['name']} ({chat_member[member]['client_id']})"
            # Create QListWidgetItem and set the name
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, chat_member[member])

            # Add the item to the list
            self.ui.memberlist.addItem(item)

    # connect to a host server
    def __connect_to_host(self, destination: str, host_name: str = None):
        # update the user information
        self.client.username = self.ui.username.text()

        # initial connect to the host
        try:
            # init a connection to the host
            # copy the callback to the connection
            self.__copy_callback_into_connection()
            # init a connection to the host
            self.thread = QThread()
            self.thread.run = (lambda: self.client.connect_to_host(destination))
            self.thread.start()
            # disable the connection plane
            self.setConnectionPlaneEnabled(False)
            while self.client.connectionID is None:
                pass
            # set the success message
            self.ui.StatusMsg.setText(f"In {host_name}, Your ID is {self.client.connectionID}")
            self.ui.connectionMsg.setText(f"Connected!")
            self.connection_type = 1
        except Exception as e:
            # set the error message
            self.ui.StatusMsg.setText("See console for more information")
            self.ui.connectionMsg.setText(f"Failed")
            print(f"Error: {e}")

    # client disconnect
    def disconnect(self):
        if self.connection_type == 0:
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
        for header in self.__header_callback_pool:
            for callback in self.__header_callback_pool[header]:
                self.client.connect_header_callback(header, callback)

    # send the message to the server
    def send_data(self, data, header: ChatHeader):
        self.client.send_data(data, header, self.event_loop)
