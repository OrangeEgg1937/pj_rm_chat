import asyncio
import json
import socket
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
        url = f"ws://{destination}"

        # create a connection data
        connection_data = ChatData(data=self.username,
                                   header=ChatHeader.INIT_CONNECTION,
                                   senderIP=self.host_ip,
                                   name=self.username)

        # connect to the host
        with connect(url) as websocket:
            # send the connection data
            websocket.send(json.dumps(connection_data.to_json()))

            # process the response
            data = websocket.recv()
            print(f"Response from the host: {data}")
            self.isConnected = True
            self.connectionID = data

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
