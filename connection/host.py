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


class ChatroomHost:
    def __init__(self, host_ip: str, host_name: str = "anonymous", port: int = 32800):
        self.host_ip = host_ip
        self.host_name = f"{host_name}_{port}"
        self.port = port
        self.__connected_clients = dict()
        self.public_list = dict()

    async def __connection_handler(self, websocket, path):
        # response to the client
        async for message in websocket:
            received_data = ChatData.from_json(message)
            print(f"[Logs] Receive a connection: {received_data.senderIP}|{received_data.name}")

            # check the header type
            if received_data.header == ChatHeader.NOP:
                print(f"Receive host alive check")
                await websocket.send("0")
                continue

            if received_data.header == ChatHeader.INIT_CONNECTION:
                # giving the client a connection ID
                new_client = ChatClientInfo(received_data.name, len(self.__connected_clients), websocket)
                self.__connected_clients[new_client.client_id] = new_client
                self.public_list[new_client.client_id] = f"{new_client.name}_{new_client.client_id}"
                await websocket.send(f"{len(self.__connected_clients) - 1}")
                # update the chatroom list to all clients
                chatroom_list = json.dumps(self.public_list)
                await self.broadcast_message(message=chatroom_list, sender=-1, header=ChatHeader.CHATROOM_LIST)
                continue

    # broadcast the message to all clients
    async def broadcast_message(self, message: str, sender: int, header: ChatHeader = ChatHeader.TEXT):
        print("[Host] Sending a message to all clients")
        # build the message
        data = ChatData(data=message, header=header, senderIP=self.host_ip, name=self.host_name)
        message = json.dumps(data.to_json())

        # send the message to all clients and checking connection
        for client in self.__connected_clients:
            try:
                await self.__connected_clients[client].websocket.send(message)
            except websockets.exceptions.ConnectionClosedError:
                print(f"Client {client} is disconnected")
                self.__connected_clients.pop(client)
                self.public_list.pop(client)

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

            async with serve(self.__connection_handler, self.host_ip, self.port):
                await asyncio.Future()  # run forever
        except Exception as e:
            print(f"Error: {e}\n Please see the error message above.")


# for script debug
if __name__ == "__main__":
    test_port = 32800

    # check argument
    parser = argparse.ArgumentParser(description="Chatroom Host")
    parser.add_argument("-p", type=int, help="Host port")
    args = parser.parse_args()
    if args.p:
        test_port = args.p

    # create a host object
    host = ChatroomHost("localhost", port=test_port)
    asyncio.run(host.start())
