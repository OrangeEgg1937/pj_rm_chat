import sys
import time
import json
import subprocess

from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QListWidget
from PyQt5.QtCore import Qt, QThread, QUrl, QObject
from PyQt5.QtWebSockets import QWebSocket
from qasync import QEventLoop

from UI.Ui_mainWindow import Ui_MainWindow
from connection.data_definition import ChatHeader, ChatData


class ClientInfo:
    def __init__(self, client_id: str, name: str):
        self.client_id = client_id
        self.name = name
        self.ip_address = "localhost"
        self.public_ip = "0.0.0.0"


class ConnectionHandler:
    def __init__(self, app: QApplication, mainWindow: QMainWindow, ui: Ui_MainWindow,
                 event_loop: QEventLoop):
        # initialize all the necessary objects
        self.app = app
        self.mainWindow = mainWindow
        self.ui = ui
        self.isConnected = 0  # 0: no yet connect, 1: connected
        self.event_loop = event_loop

        # initialize the client info
        self.client = ClientInfo("0", "anonymous")

        # initialize the connection object
        self.__header_callback_pool = None

        def __onConnected():
            print("Connected to the chatroom server, initializing the client info to the server")
            # update the client information
            self.client.ip_address = self.qtWebSocket.peerAddress().toString()
            self.client.name = self.ui.username.text()
            # create a connection data
            connection_data = ChatData(data=self.client.name,
                                       header=ChatHeader.INIT_CONNECTION,
                                       senderIP=self.client.ip_address,
                                       name=self.client.name)
            sending_data = json.dumps(connection_data.to_json())
            # send the connection data to the server
            self.qtWebSocket.sendTextMessage(sending_data)
            self.isConnected = 1

        def __onDisconnected():
            # clean up the connection
            print("Disconnected from the chatroom server")
            self.setConnectionPlaneEnabled(True)
            self.isConnected = 0

        self.qtWebSocket = QWebSocket()
        self.qtWebSocket.connected.connect(__onConnected)
        self.qtWebSocket.disconnected.connect(__onDisconnected)
        self.qtWebSocket.textMessageReceived.connect(self.__onHostDataReceived)

        # host searching socket
        self.__request_message = ChatData(data=self.client.name,
                                          header=ChatHeader.REQUEST_HOST_LIST,
                                          senderIP=self.client.ip_address,
                                          name=self.client.name)
        self.__search_socket = QWebSocket()

        def __onRequestServerReady():
            print("[Client] Requesting host list...")
            self.__search_socket.sendTextMessage(json.dumps(self.__request_message.to_json()))

        self.__search_socket.connected.connect(__onRequestServerReady)
        self.__search_socket.disconnected.connect(lambda: print("Disconnected from the search server"))
        self.__search_socket.textMessageReceived.connect(self.__onReceivedHostList)

        # create chatroom socket
        self.__create_chatroom_message = None
        self.__create_chatroom_socket = QWebSocket()
        self.__create_chatroom_socket.connected.connect(self.__onCreateChatroomServerConnected)
        self.__create_chatroom_socket.disconnected.connect(self.__onCreateChatroomServerDisconnected)
        self.__create_chatroom_socket.textMessageReceived.connect(self.__onCreateChatroomServerReceived)

        # register the signal
        self.ui.connectBtn.clicked.connect(self.__onConnectButtonClicked)
        self.ui.connectToLocalhost.clicked.connect(lambda: self.__onConnectButtonClicked(1))

        self.ui.hostBtn.clicked.connect(self.__onHostButtonClicked)

        self.ui.connect_to_chat.clicked.connect(self.__onConnectToChatButtonClicked)

        # self.ui.disconnect_btn.clicked.connect(self.disconnect)

        # init the header callback
        self.__header_callback = None
        self.__init_header_callback()

        # add the function to the header callback
        self.connect_header_callback(ChatHeader.CHATROOM_LIST, self.update_member_list)

    # connect button clicked
    def __onConnectButtonClicked(self, method: int = 0):
        # check the user option type, 0 means connect with the input IP address, 1 means connect to the localhost
        if method == 0:
            destination = f"ws://{self.ui.target_ip.text()}:60000"
        else:
            destination = "ws://localhost:60000"

        # connect to the host
        self.__search_socket.open(QUrl(destination))

    def __onHostButtonClicked(self):
        # get the IP address
        ip_address = self.ui.target_ip.text()
        # building a json message
        message = {
            "chatroom_name": self.ui.chatroom_name.text(),
            "port": self.ui.chatroom_port.text(),
            "chatroom_server_ip": self.ui.target_ip.text(),
            "host_ip": self.ui.public_ip.text(),
            "local_ip": self.ui.local_ip.text()
        }
        message = json.dumps(message)
        # send a message to the chatroom server to create a chatroom
        self.__create_chatroom_message = ChatData(data=message,
                           header=ChatHeader.CLIENT_HOST_CHATROOM,
                           senderIP=self.client.ip_address,
                           name=self.client.name)

        # connect to the chatroom server
        self.__create_chatroom_socket.open(QUrl(f"ws://{ip_address}:60000"))

    def __onCreateChatroomServerConnected(self):
        # send the message to the chatroom server
        self.__create_chatroom_socket.sendTextMessage(json.dumps(self.__create_chatroom_message.to_json()))

    def __onCreateChatroomServerDisconnected(self):
        pass

    def __onCreateChatroomServerReceived(self, message: str):
        # get the message
        if message == "OK":
            print("Chatroom created successfully")
            self.ui.StatusMsg.setText("Chatroom created successfully")
        else:
            print("Chatroom creation failed")
            self.ui.StatusMsg.setText("Chatroom created failed")

    def __onHostOnLocalhostButtonClicked(self):
        pass


    def __onConnectToChatButtonClicked(self):
        if self.ui.chatroom_list.currentItem() is None:
            return
        # get the selected item from the list
        selected_item = self.ui.chatroom_list.currentItem().data(Qt.UserRole)

        # if the selected item is None or unknown object, then return
        if selected_item is None:
            return

        # print the selected item
        print(f"Selected item-IP address: {selected_item}")

        # connect to the host
        self.qtWebSocket.open(QUrl(f"ws://{selected_item}"))

    # search the host
    def __onReceivedHostList(self, message: str):
        # get the host list
        host_list = json.loads(json.loads(message)['data'])

        print(host_list)

        # update the UI
        self.ui.chatroom_list.clear()

        for host in host_list:
            print(host_list[host]['name'])
            # Create QListWidgetItem and set the name
            item = QListWidgetItem(host_list[host]['name'])
            item.setData(Qt.UserRole, host_list[host]['senderIP'])

            # Add the item to the list
            self.ui.chatroom_list.addItem(item)

        # close the connection
        self.__search_socket.close()

    def __onHostDataReceived(self, message: str):
        # if the message is a digit/int, then it is the connection ID
        if message.isdigit():
            self.client.client_id = message
            print(f"Connection ID: {message}")
            return

        # get the package data
        data = ChatData.from_json(message)
        print(f"[Client] Received a message from {data.name}")

        # process the header callback
        self.__process_header_callback(data.header, data)

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
            name = f"{chat_member[member]['name']} ({chat_member[member]['client_id']})"
            # Create QListWidgetItem and set the name
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, chat_member[member])

            # Add the item to the list
            self.ui.memberlist.addItem(item)

    # send the message to the server
    def send_data(self, data, header: ChatHeader):
        # build the message
        data = ChatData(data=data, header=header, senderIP=self.client.ip_address, name=self.client.name)
        message = json.dumps(data.to_json())
        print(f"[Client] Sending {data.header} message")
        sent = self.qtWebSocket.sendTextMessage(message)
        print(f"[Client] Sent: {sent}")

    '''
        Following is the header callback implementation
    '''
    # init the header_callback variable
    def __init_header_callback(self):
        self.__header_callback = dict()
        for headerType in ChatHeader:
            self.__header_callback[headerType] = []

    # add a callback to the header
    def connect_header_callback(self, header: ChatHeader, callback):
        if self.__header_callback is None:
            self.__init_header_callback()
        if header not in self.__header_callback:
            raise ValueError(f"Header {header} is not in the header list")
        self.__header_callback[header].append(callback)

    # remove a callback from the header
    def disconnect_header_callback(self, header: ChatHeader, callback):
        if self.__header_callback is None:
            self.__init_header_callback()
        if header not in self.__header_callback:
            raise ValueError(f"Header {header} is not in the header list")
        self.__header_callback[header].remove(callback)

    # process the header callback
    def __process_header_callback(self, header: ChatHeader, data):
        if header not in self.__header_callback:
            return
        for callback in self.__header_callback[header]:
            callback(data)