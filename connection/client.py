import asyncio
import json
import socket
from connection.data_definition import ChatHeader, ChatData
from websockets.sync.client import connect


# define the Client class
class ChatroomClient:
    def __init__(self, host_ip, port: str = "a", username: str = "anonymous"):
        self.host = f"ws://{host_ip}:{port}"  # forming a host connection address
        self.username = username
        self.hostList = dict()
        self.isReady = False

    # see all available host
    async def request_host_list(self):
        async with connect(self.host) as websocket:
            data = websocket.recv()
            server_info = ChatData.from_json(data)

            # check the server is in the set or not
            if server_info.senderIP not in self.hostList:
                self.hostList[server_info.senderIP] = server_info
                print(f"New host found: {server_info.senderIP}: {server_info.name}")
            else:
                print(f"Host {server_info.senderIP} is already in the list")


def demo_test():
    with connect("ws://localhost:32800") as websocket:
        data = ChatData("Hello World!", ChatHeader.TEXT, 5)
        # convert data into json
        json_data = json.dumps(data.to_json())
        websocket.send(json_data)
        message = websocket.recv()
        print(f"Received: {message}")


# script debug
if __name__ == "__main__":
    demo_test()
