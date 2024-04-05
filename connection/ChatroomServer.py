import asyncio
import websockets
import json
from connection.data_definition import ChatHeader, ChatData

IP_ADDRESS = "localhost"
PORT = 60000


# The RegistryServer class is a server that keeps track of all active hosts in the network.
class ChatroomServer:
    def __init__(self, host_ip, port):
        self.hostList = dict()
        self.host_ip = host_ip
        self.port = port

    async def __connection_handler(self, websocket, path):
        # response to the client
        async for message in websocket:
            received_data = ChatData.from_json(message)
            print(f"[New Connection] Receive a connection: {received_data.senderIP}|{received_data.name}")

            # check the received data header
            if received_data.header == ChatHeader.REQUEST_HOST_LIST:
                hostList = json.dumps(self.hostList, default=ChatData.default_to_json)
                data = ChatData(data=hostList,
                                header=ChatHeader.REQUEST_HOST_LIST,
                                senderIP=self.host_ip,
                                name="ChatroomServer")
                send_data = json.dumps(data.to_json())
                await websocket.send(send_data)
                continue

            # register a chatroom host
            if received_data.header == ChatHeader.REGISTER_HOST:
                message = "OK"
                # check the host is in the set or not
                if received_data.senderIP not in self.hostList:
                    self.hostList[received_data.senderIP] = received_data
                    print(f"New host found: {received_data.senderIP}: {received_data.name}")
                else:
                    print(f"Host {received_data.senderIP} is already in the list")
                    message = "[Chatroom Server] The IP/Port is already used! Please try another one!"  # Error message

                await websocket.send(message)
                continue

    # check host connection (heartbeat mechanism)
    async def check_host_connection(self):
        while True:
            await asyncio.sleep(5)  # every 5 seconds to do the checking
            print("[Server] Task: Checking host connection")
            for host in list(self.hostList):
                try:
                    print(f"[Server] Checking {host}")
                    async with websockets.connect(f"ws://{host}", timeout=5) as websocket:
                        pong_waiter = await websocket.ping()
                        latency = await pong_waiter
                        print(f"[Server] {host} is still connected, latency:{latency}")
                except Exception as e:
                    print(f"[Server] Host {host} is disconnected: {e}")
                    del self.hostList[host]

    def start(self):
        try:
            start_server = websockets.serve(self.__connection_handler, self.host_ip, self.port)
            asyncio.get_event_loop().run_until_complete(start_server)
            asyncio.get_event_loop().create_task(self.check_host_connection())
            print(f"Chatroom server is running on ws://{self.host_ip}:{self.port}")
            asyncio.get_event_loop().run_forever()
        except Exception as e:
            print(f"Error: {e}\n The IP address or port is already in use. Please try another one.")


if __name__ == "__main__":
    # start the server
    chatroom_server = ChatroomServer(IP_ADDRESS, PORT)
    asyncio.run(chatroom_server.start())
