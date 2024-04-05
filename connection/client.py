import asyncio
import json
import socket
import websockets
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
        self.buffer = None
        self.__header_callback = None

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
            print(f"[NOP] Header {header} is not in the header list")
            return
        print(f"Processing header callback function: {header}")
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
        asyncio.run(self.__listener())

    # listen to the host incoming message
    async def __listener(self):
        # starting a connection to the host
        try:
            async with websockets.connect(f"ws://{self.destination}") as ws:
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
                        await ws.send(sending_data)

                    # receive the message
                    message = await ws.recv()

                    # initial connection checking
                    if self.__isConnected is False:
                        if message.isdigit():
                            self.__isConnected = True
                            self.connectionID = int(message)
                            print(f"Connection ID: {self.connectionID}")
                            continue

                    package = ChatData.from_json(message)
                    print(f"Received a message from {package.senderIP}: {package.data}")

                    # process the header callback
                    self.__process_header_callback(package.header, package)

        except websockets.exceptions.ConnectionClosedOK:
            print(f"Connection closed: {self.destination}")
        except websockets.exceptions.ConnectionClosedError:
            print(f"Connection closed incorrectly: {self.destination}")
        # clean up the connection
        await self.websocket.close()
        self.__isConnected = False
        self.connectionID = None
        self.buffer = None
        print(f"Client disconnected from {self.destination}")
        self.websocket = None

    # general data transfer to the host, if there is a data received, it will be stored in the buffer
    def send_data(self, data: str, header: ChatHeader):
        # create a connection data
        connection_data = ChatData(data=data,
                                   header=header,
                                   senderIP=self.host_ip,
                                   name=self.username)

        # send the connection data
        current_event_loop = asyncio.get_event_loop()
        current_event_loop.create_task(self.websocket.send(json.dumps(connection_data.to_json())))

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
