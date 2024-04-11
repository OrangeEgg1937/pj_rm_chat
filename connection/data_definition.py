from enum import Enum
import json
import base64


# define the Chat data type
class ChatHeader(Enum):
    NOP = 0
    INIT_CONNECTION = 1
    AUDIO = 2
    TEXT = 3
    VIDEO = 4
    REQUEST_HOST_LIST = 5
    REGISTER_HOST = 6
    CHATROOM_LIST = 7
    RECORDING = 8
    DONE_RECORDING = 9
    RECORDING_FILE = 10
    RECORDING_FILE_NAME = 11
    REQUEST_RECORDING_FILE = 12
    KARAOKE_SONG_NAME = 17
    KARAOKE_SONG = 13
    KARAOKE_SONG_LIST = 14
    KARAOKE_STOP = 15
    KARAOKE_START = 16
    KARAOKE_SONG_TRACKS = 18


# define the Chat data
class ChatData:
    # Construct by data, header, and connectionID
    def __init__(self, data, header: ChatHeader, senderIP: str, name: str = "anonymous"):
        self.data = data
        self.header = header
        self.senderIP = senderIP
        self.name = name

    # Construct by a json object
    @classmethod
    def from_json(cls, receive, process=-1):
        data = json.loads(receive)

        # if header is audio, convert the data to bytes
        if data["header"] == ChatHeader.AUDIO.value:
            data["data"] = base64.b64decode(data["data"])

        if process == -1:
            # auto check the header type
            if data["header"] == ChatHeader.TEXT.value:
                process = 0

        if process == 1:
            server_data = json.loads(data["data"])
            return cls(data=server_data,
                       header=ChatHeader(data["header"]),
                       senderIP=data["senderIP"],
                       name=data["name"])

        return cls(data=data["data"],
                   header=ChatHeader(data["header"]),
                   senderIP=data["senderIP"],
                   name=data["name"])

    def to_json(self):
        # encode to 64 if the data bytes
        if isinstance(self.data, bytes):
            self.data = base64.b64encode(self.data).decode('utf-8')
        return {
            "data": self.data,
            "header": self.header.value,
            "senderIP": self.senderIP,
            "name": self.name
        }

    @staticmethod
    def default_to_json(obj):
        if isinstance(obj, ChatData):
            return obj.to_json()

        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")
