import asyncio
import json
from datetime import datetime
import time
import pytz
import zlib
import threading

import base64
import websockets
import argparse
import os

from connection.data_definition import ChatHeader, ChatData
from websockets.server import serve

CHATROOM_SERVER_ADDR = "43.198.17.189"


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
    def __init__(self, host_ip: str, host_name: str, port: int = 32800, local_address="localhost",
                 chatroom_server_ip="localhost"):
        self.setuptime = time.time()
        self.host_ip = host_ip
        self.port = port
        self.__connected_clients = set()
        self.public_list = dict()
        self.currentID = 1
        self.isHosted = False
        self.host_name = host_name
        self.local_address = local_address
        self.chatroom_server_ip = chatroom_server_ip

        # ONLY FOR AWS TESTING SERVER
        # self.dummy_client = ChatClientInfo("Repeater", 0, None)
        # self.public_list[0] = self.dummy_client

        # recording
        self.recording_file_dir = f"./recording/rm_{self.setuptime}"
        self.current_recording_file_list = []
        self.__init_recording_fileDir()
        self.__incoming_filename = dict()

        # karaoke song list
        self.karaoke_song_dir = "../vocal_audio"
        self.karaoke_song_list = dict()
        self.__incoming_karaoke_song_name = dict()
        self.isKaraokePlaying = False

        # timeout counter
        self.timeout_counter = 0

    def __init_recording_fileDir(self):
        try:
            os.makedirs(self.recording_file_dir)
        except FileExistsError:
            print(f"[Host - Recording] Directory already exists: {self.recording_file_dir}")

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
                    print(
                        f"[Host - New Connection] New client connected: {data.name}, it assigned with:ID={self.currentID}")
                    # send a connection ID to the client
                    await websocket.send(str(self.currentID))
                    # broadcast the new chatroom list to all client
                    print(f"Current public list: {self.public_list}")
                    chatroom_list = json.dumps(
                        {client_id: client_info.to_json() for client_id, client_info in self.public_list.items()})
                    print(f"Current public list: {chatroom_list}")
                    self.currentID = self.currentID + 1
                    await self.broadcast_message(chatroom_list, ChatHeader.CHATROOM_LIST)
                elif data.header == ChatHeader.AUDIO:
                    currentDateAndTime = datetime.now(pytz.utc)
                    print(f"[Host - Audio] Received an audio from {data.name}, {data.senderIP}, size:{len(data.data)}, t={currentDateAndTime}")
                    # get the sender ID by the current websocket
                    senderID = None
                    for client in list(self.public_list):
                        if self.public_list[client].websocket == websocket:
                            senderID = client
                            break
                    # broadcast the message to all clients
                    await self.broadcast_message(f"[System]: I hear {data.name} you are speaking.", ChatHeader.TEXT)
                    await self.broadcast_message(data.data, ChatHeader.AUDIO, websocket, senderID)
                elif data.header == ChatHeader.RECORDING:
                    print("Receive recording header")
                    await self.broadcast_message('', ChatHeader.RECORDING)
                elif data.header == ChatHeader.DONE_RECORDING:
                    print("Receive DONE recording header")
                    await self.broadcast_message('', ChatHeader.DONE_RECORDING)
                elif data.header == ChatHeader.RECORDING_FILE_NAME:
                    print(f"[Host - Recording] Received a recording file name: {data.data}")
                    self.__incoming_filename[websocket] = data.data
                elif data.header == ChatHeader.RECORDING_FILE:
                    await self.broadcast_message('[System]: Received a audio file', ChatHeader.TEXT)
                    # convert the bytes to a .wav file
                    filename = self.__incoming_filename[websocket]
                    # convert the base64 data back to bytes
                    recording = base64.b64decode(data.data)
                    # decompress the data
                    recording = zlib.decompress(recording)
                    with open(f"{self.recording_file_dir}/{filename}", "wb") as file:
                        file.write(recording)
                        file.close()
                    # add the file into file list
                    self.current_recording_file_list.append(filename)
                    # broadcast the new file list to all client
                    await self.broadcast_message(json.dumps(self.current_recording_file_list), ChatHeader.RECORDING_FILE)
                elif data.header == ChatHeader.REQUEST_RECORDING_FILE:
                    # get the requested file name
                    filename = data.data
                    # check if the file is in the list
                    if filename in self.current_recording_file_list:
                        # send the file to the client
                        with open(f"{self.recording_file_dir}/{filename}", "rb") as file:
                            # read the file
                            file_data = file.read()
                            # compress the data
                            file_data = zlib.compress(file_data)
                            # packing the data
                            message = ChatData(data=file_data, header=ChatHeader.REQUEST_RECORDING_FILE, senderIP=self.host_ip,
                                               name=self.host_name)
                            # convert the message to json
                            message = json.dumps(message.to_json())
                            await websocket.send(message)
                            file.close()
                    else:
                        message = ChatData(data="[System]: File not found", header=ChatHeader.TEXT, senderIP=self.host_ip, name=self.host_name)
                        message = json.dumps(message.to_json())
                        await websocket.send(message)
                elif data.header == ChatHeader.KARAOKE_SONG_NAME:
                    print(f"[Host - Karaoke] Received a karaoke song name: {data.data}")
                    self.__incoming_karaoke_song_name[websocket] = data.data
                elif data.header == ChatHeader.KARAOKE_SONG:
                    print(f"[Host - Karaoke] Received a karaoke song data")
                    # get the song name
                    song_name = self.__incoming_karaoke_song_name[websocket]
                    # convert the base64 data back to bytes
                    song_data = base64.b64decode(data.data)
                    # decompress the data
                    song_data = zlib.decompress(song_data)
                    # save the song to the path
                    self.add_karaoke_song(song_name, song_data)
                    # broadcast the new song list to all client
                    song_list = json.dumps(self.karaoke_song_list)
                    await self.broadcast_message(song_list, ChatHeader.KARAOKE_SONG_LIST)
                elif data.header == ChatHeader.KARAOKE_START:
                    print(f"[Host - Karaoke] Received a karaoke start request: {data.data}")
                    if self.isKaraokePlaying:
                        return # if the karaoke is playing, then ignore the request
                    # check if the song is in the list
                    if data.data in self.karaoke_song_list:
                        # get the song path
                        song_path = self.karaoke_song_list[data.data]
                        # send the song to all clients
                        await self.broadcast_message(song_path, ChatHeader.KARAOKE_START)
                        self.isKaraokePlaying = True
                        # start the karaoke song broadcast thread
                        threading.Thread(target=self.__broadcast_song, args=(song_path,)).start()
                    else:
                        print("[Host - Karaoke] Song not found")
                elif data.header == ChatHeader.KARAOKE_STOP:
                    print(f"[Host - Karaoke] Received a karaoke stop request: {data.data}")
                    self.isKaraokePlaying = False
                    await self.broadcast_message("", ChatHeader.KARAOKE_STOP)
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
            chatroom_list = json.dumps(
                {client_id: client_info.to_json() for client_id, client_info in self.public_list.items()})
            await self.broadcast_message(chatroom_list, ChatHeader.CHATROOM_LIST)
        else:
            # check the number of people in the chatroom, if no one is in the chatroom, timeout counter add 1
            if len(self.__connected_clients) == 0:
                self.timeout_counter += 1
            print(f"[Host - OnClear] Timeout counter: {self.timeout_counter}")
            if self.timeout_counter >= 5:
                print(f"[Host - OnClear] Timeout counter reached 10, closing the host application")
                os._exit(0)

    def __broadcast_song(self, song_path):
        # separating the song byte into different parts
        with open(song_path, "rb") as file:
            song_data = file.read()
            file.close()

        # compress the data
        song_data = zlib.compress(song_data)

        # send the song to all clients with every 30000 bytes
        for i in range(0, len(song_data), 30000):
            # check the isPlaying value
            if not self.isKaraokePlaying:
                return
            # get the data
            data = song_data[i:i + 30000]
            # send the data to all clients
            self.broadcast_message(data, ChatHeader.KARAOKE_SONG)

    # adding a song to the karaoke list
    def add_karaoke_song(self, song_name, song_data):
        # convert the song_data into a file
        with open(f"{self.karaoke_song_dir}/{song_name}", "wb") as file:
            file.write(song_data)
            file.close()

        # add the song to the list
        self.karaoke_song_list[song_name] = f"{self.karaoke_song_dir}/{song_name}"

    # broadcast the message to all clients OR broadcast the message to all clients except the sender
    async def broadcast_message(self, message: str, header: ChatHeader = ChatHeader.TEXT, ignoreSender=None, senderID=None):
        print("[Host- Broadcast] Sending a message to all clients")

        senderName = self.host_ip
        if senderID is not None:
            senderName = senderID

        # build the message
        data = ChatData(data=message, header=header, senderIP=senderName, name=self.host_name)
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
            async with websockets.connect(f"ws://{self.chatroom_server_ip}:60000") as websocket:
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

                async with serve(self.__connection_handler, self.local_address, self.port):
                    await asyncio.Future()  # run forever
        except Exception as e:
            self.isHosted = False
            raise Exception(f"{e}\nPlease see the error message above.")


# for script debug
if __name__ == "__main__":
    # check the argument
    parser = argparse.ArgumentParser()
    parser.add_argument("-ip", "--host_ip", help="The host IP address", default="43.198.17.189")
    parser.add_argument("-port", "--host_port", help="The host port", default=32800)
    parser.add_argument("-name", "--host_name", help="The host name", default="AWS_rm0")
    parser.add_argument("-local", "--host_local", help="The host local address", default="172.31.13.35")
    parser.add_argument("-c", "--cserver_ip", help="The host local address", default="43.198.17.189")

    args = parser.parse_args()

    chatroom = ChatroomHost(args.host_ip, args.host_name, args.host_port, args.host_local, args.cserver_ip)

    # start the chatroom
    asyncio.run(chatroom.start())