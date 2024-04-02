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
        self.isReady = False
        self.request_info = ChatData(data=self.username,
                                     header=ChatHeader.REQUEST_HOST_LIST,
                                     senderIP=self.host_ip,
                                     name=self.username)

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


# script debug
if __name__ == "__main__":
    temp = ChatroomClient("localhost", port=60000)
    temp.request_host_list()
