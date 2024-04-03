import asyncio
import json
import socket
import websockets
from connection.data_definition import ChatHeader, ChatData
from websockets.sync.client import connect


# define the Client class
class ChatroomClient:
    def __init__(self, host_ip, port: str = "a", username: str = "anonymous"):
        self.host_ip = f"ws://{host_ip}:{port}"  # forming a host connection address
        self.username = username
        self.hostList = dict()
        self.isConnected = False
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

        # create a connection data
        connection_data = ChatData(data=self.username,
                                   header=ChatHeader.INIT_CONNECTION,
                                   senderIP=self.host_ip,
                                   name=self.username)

        # start the listener
        asyncio.run(self.__listener())

    # listen to the host incoming message
    async def __listener(self):
        # connect to the host
        async with websockets.connect(f"ws://{self.destination}") as websocket:
            # create a connection data
            connection_data = ChatData(data=self.username,
                                       header=ChatHeader.INIT_CONNECTION,
                                       senderIP=self.host_ip,
                                       name=self.username)
            # send the connection data
            await websocket.send(json.dumps(connection_data.to_json()))

            print(f"client connected to {self.destination}")

            # get the connection ID first
            data = await websocket.recv()
            self.connectionID = int(data)
            self.isConnected = True

            print(f"client received a ID: {data}")

            # start listening to the host incoming message
            async for message in websocket:
                received_data = ChatData.from_json(message)
                self.buffer = received_data.data
                print(f"Received data: {self.buffer}")

    # general data transfer to the host, if there is a data received, it will be stored in the buffer
    def send_data(self, data: str, header: ChatHeader):
        # create a connection data
        connection_data = ChatData(data=data,
                                   header=header,
                                   senderIP=self.host_ip,
                                   name=self.username)

        # connect to the host
        with connect(self.destination) as websocket:
            # send the connection data
            websocket.send(json.dumps(connection_data.to_json()))

            # process the response
            data = websocket.recv()
            print(f"Response from the host: {data}")

            self.buffer = data


# script debug
if __name__ == "__main__":
    temp = ChatroomClient("localhost", port=60000)
    temp.request_host_list()
