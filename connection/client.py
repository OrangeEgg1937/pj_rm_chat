import asyncio
import json
import socket
import websockets
import queue
import threading
from connection.data_definition import ChatHeader, ChatData
from websockets.sync.client import connect


# define the Client class
class ChatroomClient:
    def __init__(self, host_ip, port: str = "a", username: str = "anonymous"):
        self.websocket = None
        self.host_ip = f"ws://{host_ip}:{port}"  # forming a host connection address
        self.username = username
        self.hostList = dict()
        self.__isConnected = False
        self.destination = None
        self.request_info = ChatData(data=self.username,
                                     header=ChatHeader.REQUEST_HOST_LIST,
                                     senderIP=self.host_ip,
                                     name=self.username)
        self.connectionID = None
        self.buffer = queue.Queue()
        self.__header_callback = None
        self.send_thread = None

        # init the header callback
        self.__init_header_callback()

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

    # see all available host
    def request_host_list(self):
        print(f"Requesting host list from {self.host_ip}")
        with connect(self.host_ip) as websocket:
            # send the request to the server
            websocket.send(json.dumps(self.request_info.to_json()))

            # process the response
            data = websocket.recv()
            server_info = ChatData.from_json(data, process=1)

            # print the data
            for ser_dat in server_info.data:
                print(f"Host: {server_info.data[ser_dat]["senderIP"]}")

            # copy the data to the host list
            self.hostList = server_info.data.copy()

    # connect to the host
    def connect_to_host(self, destination: str):
        # update the destination
        self.destination = destination

        # start the listener
        self.__listener()

    # a thread for sending data to the host
    def __send_data_thread(self):
        while True:
            if self.__isConnected is False:
                break
            if self.buffer is not None:
                data = self.buffer.get()
                if data is not None:
                    print(f"Get one data, sending out... (size of buffer: {self.buffer.qsize()})")
                    self.websocket.send(data)

    # listen to the host incoming message
    def __listener(self):
        # starting a connection to the host
        try:
            with connect(f"ws://{self.destination}") as ws:
                self.websocket = ws
                while True:
                    if (self.__isConnected is False) and (self.connectionID is None):
                        # create a connection data
                        connection_data = ChatData(data=self.username,
                                                   header=ChatHeader.INIT_CONNECTION,
                                                   senderIP=self.host_ip,
                                                   name=self.username)
                        sending_data = json.dumps(connection_data.to_json())
                        # send the connection ID to the host
                        ws.send(sending_data)

                    # receive the message
                    message = ws.recv()

                    if message is None:
                        continue

                    # initial connection checking
                    if self.__isConnected is False:
                        if message.isdigit():
                            self.__isConnected = True
                            self.connectionID = int(message)
                            # starting the sending data thread
                            self.send_thread = threading.Thread(target=self.__send_data_thread)
                            self.send_thread.start()
                            continue

                    package = ChatData.from_json(message)

                    # process the header callback
                    self.__process_header_callback(package.header, package)

        except websockets.exceptions.ConnectionClosedOK:
            print(f"Connection closed: {self.destination}")
        except websockets.exceptions.ConnectionClosedError:
            print(f"Connection closed incorrectly: {self.destination}")
        # clean up the connection
        self.websocket.close()
        self.__isConnected = False
        self.connectionID = None
        self.buffer = None
        print(f"Client disconnected from {self.destination}")
        self.websocket = None
        # clean the thread
        self.send_thread = None

    # general data transfer to the host, if there is a data received, it will be stored in the buffer
    def send_data(self, data: str, header: ChatHeader):
        # create a connection data
        connection_data = ChatData(data=data,
                                   header=header,
                                   senderIP=self.host_ip,
                                   name=self.username)

        # put the data into the buffer
        self.buffer.put(json.dumps(connection_data.to_json()))

    # disconnect the client from the host
    async def disconnect(self):
        if self.websocket is not None:
            await self.websocket.close()
            self.__isConnected = False
            self.connectionID = None
            self.buffer = None
            print(f"Client disconnected from {self.destination}")
            self.websocket = None


# script debug
if __name__ == "__main__":
    chatroom_user = ChatroomClient("localhost", port=60000)
    chatroom_user.connect_to_host("localhost:32800")
