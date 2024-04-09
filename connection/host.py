import asyncio
import json
import websockets
import argparse
from connection.data_definition import ChatHeader, ChatData
from websockets.server import serve

class ChatClientInfo:
    def __init__(self, name, client_id, websocket):
        self.name = name
        self.client_id = client_id
        self.websocket = websocket

    def to_json(self):
        return {
            "name": self.name,
            "client_id": self.client_id
        }


class ChatroomHost:
    def __init__(self, host_ip: str, host_name: str, port: int = 32800):
        self.host_ip = host_ip
        self.port = port
        self.__connected_clients = set()
        self.public_list = dict()
        self.currentID = 0
        self.isHosted = False
        self.host_name = host_name

    async def __connection_handler(self, websocket, path):
        # when there is a connection, hold it
        while True:
            try:
                print(f"[Host] Connection from {websocket}")
                message = await websocket.recv()  # receive the message
                data = ChatData.from_json(message)  # decode the message
                if data.header == ChatHeader.TEXT:
                    print(f"[Host - Text] Received a message from {data.name}: {data.data}")
                    # broadcast the message to all clients
                    await self.broadcast_message(data.data, ChatHeader.TEXT)
                elif data.header == ChatHeader.INIT_CONNECTION:
                    self.__connected_clients.add(websocket)  # add the client to the list
                    # assign the client ID if the currentID is not in the list
                    while self.currentID in self.public_list:
                        self.currentID = self.currentID + 1
                    # create a new client information
                    client_info = ChatClientInfo(data.data, self.currentID, websocket)
                    self.public_list[self.currentID] = client_info
                    print(f"[Host - New Connection] New client connected: {data.name}, it assigned with:ID={self.currentID}")
                    # send a connection ID to the client
                    await websocket.send(str(self.currentID))
                    # broadcast the new chatroom list to all client
                    print(f"Current public list: {self.public_list}")
                    chatroom_list = json.dumps({client_id: client_info.to_json() for client_id, client_info in self.public_list.items()})
                    print(f"Current public list: {chatroom_list}")
                    self.currentID = self.currentID + 1
                    await self.broadcast_message(chatroom_list, ChatHeader.CHATROOM_LIST)
                elif data.header == ChatHeader.AUDIO:
                    print(f"[Host - Audio] Received an audio from {data.name}, {data.senderIP}")
                    # broadcast the message to all clients
                    await self.broadcast_message(data.data, ChatHeader.AUDIO, websocket)

            except websockets.exceptions.ConnectionClosedOK:
                print(f"[Host - OnClose] Connection closed: {websocket}")
                break
            except websockets.exceptions.ConnectionClosed:
                print(f"[Host - OnClose] Connection closed incorrectly: {websocket}")
                break
        # clean up the connection
        if websocket in self.__connected_clients:
            print(f"[Host - OnClear] Cleaning up the connection: {websocket}")
            print(f"[Host - OnClear] Cleaning up the connection: {self.__connected_clients}")
            self.__connected_clients.remove(websocket)
            print(f"[Host - OnClear] Cleaning up the connection: {self.__connected_clients}")
            print(f"Removed client: {websocket}")
            for client in list(self.public_list):
                print(f"Selected client{self.public_list[client].websocket}")
                if self.public_list[client].websocket == websocket:
                    self.public_list.pop(client)
            # broadcast the new chatroom list to all client
            chatroom_list = json.dumps({client_id: client_info.to_json() for client_id, client_info in self.public_list.items()})
            await self.broadcast_message(chatroom_list, ChatHeader.CHATROOM_LIST)

    # broadcast the message to all clients OR broadcast the message to all clients except the sender
    async def broadcast_message(self, message: str, header: ChatHeader = ChatHeader.TEXT, ignoreSender=None):
        print("[Host- Broadcast] Sending a message to all clients")

        # build the message
        data = ChatData(data=message, header=header, senderIP=self.host_ip, name=self.host_name)
        message = json.dumps(data.to_json())

        # copy the list
        receiver_list = self.__connected_clients.copy()

        # check the value of sender
        if ignoreSender is not None:
            # remove the sender from the list
            receiver_list.remove(ignoreSender)

        # send the message to all clients and checking connection
        try:
            websockets.broadcast(receiver_list, message)
        except websockets.exceptions.ConnectionClosedOK:
            print(f"One Client is disconnected")

    async def start(self):
        print(f"Host name {self.host_name} ({self.host_ip}:{self.port}) is starting...")
        try:
            # init a host information to Chatroom server
            async with websockets.connect(f"ws://{self.host_ip}:60000") as websocket:
                data = ChatData(data=json.dumps(self.host_name),
                                header=ChatHeader.REGISTER_HOST,
                                senderIP=f"{self.host_ip}:{self.port}",
                                name=self.host_name)
                await websocket.send(json.dumps(data.to_json()))
                response = await websocket.recv()
                print(f"Response from server: {response}")

                # if the response is not ok, then close the connection
                if response != "OK":
                    raise Exception("Connection failed/Port already used. Please try another one.")

                self.isHosted = True

                async with serve(self.__connection_handler, self.host_ip, self.port):
                    await asyncio.Future()  # run forever
        except Exception as e:
            self.isHosted = False
            raise Exception(f"{e}\nPlease see the error message above.")


# for script debug
if __name__ == "__main__":
    # check the argument
    parser = argparse.ArgumentParser()
    parser.add_argument("-ip", "--host_ip", help="The host IP address", default="localhost")
    parser.add_argument("-port", "--host_port", help="The host port", default=32801)
    parser.add_argument("-name", "--host_name", help="The host name", default="Host")

    args = parser.parse_args()

    chatroom = ChatroomHost(args.host_ip, args.host_name, args.host_port)

    # start the chatroom
    asyncio.run(chatroom.start())
