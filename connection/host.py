import asyncio
import json
import websockets
import threading
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
    def __init__(self, host_ip: str, host_name: str = "anonymous", port: int = 32800):
        self.host_ip = host_ip
        self.host_name = f"{host_name}_{port}"
        self.host_info = ChatClientInfo(self.host_name, 0, None)
        self.port = port
        self.__connected_clients = set()
        self.public_list = dict()
        self.currentID = 1
        self.isHosted = False
        self.__header_callback = None

        # init the header callback
        self.__init_header_callback()

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

    # broadcast the message to all clients
    async def broadcast_message(self, message: str, header: ChatHeader = ChatHeader.TEXT):
        print("[Host- Broadcast] Sending a message to all clients")

        # build the message
        data = ChatData(data=message, header=header, senderIP=self.host_ip, name=self.host_name)
        message = json.dumps(data.to_json())

        # thread callback the header
        callback_threading = threading.Thread(target=self.__process_header_callback, args=(header, data))
        callback_threading.start()

        # send the message to all clients and checking connection
        try:
            websockets.broadcast(self.__connected_clients, message)
        except websockets.exceptions.ConnectionClosedOK:
            print(f"One Client is disconnected")

    async def start(self):
        print(f"Host: {self.host_name} is starting...")
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

                # adding itself into the host list
                self.public_list[0] = self.host_info

                async with serve(self.__connection_handler, self.host_ip, self.port):
                    await asyncio.Future()  # run forever
        except Exception as e:
            self.isHosted = False
            raise Exception(f"{e}\nPlease see the error message above.")

    # define the host header_callback variable
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


# for script debug
if __name__ == "__main__":
    chatroom = ChatroomHost("localhost")

    # start the chatroom
    asyncio.run(chatroom.start())
