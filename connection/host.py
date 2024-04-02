import asyncio
import json
import websockets
import sys
import argparse
from connection.data_definition import ChatHeader, ChatData
from websockets.server import serve


class ChatroomHost:
    def __init__(self, host_ip: str, host_name: str = "anonymous", port: int = 32800):
        self.host_ip = host_ip
        self.host_name = f"{host_name}_{port}"
        self.port = port
        self.connected_clients = set()

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
                self.connected_clients.add(websocket)
                await websocket.send("You are connected to this chat room")
                continue

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
