from enum import Enum
import json


# define the Chat data type
class ChatHeader(Enum):
    NOP = 0
    INIT_CONNECTION = 1
    AUDIO = 2
    TEXT = 3
    VIDEO = 4
    REQUEST_HOST_LIST = 5
    REGISTER_HOST = 6


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
    def from_json(cls, receive):
        data = json.loads(receive)
        return cls(data=data["data"],
                   header=ChatHeader(data["header"]),
                   senderIP=data["senderIP"],
                   name=data["name"])

    def to_json(self):
        return {
            "data": self.data,
            "header": self.header.value,
            "senderIP": self.senderIP,
            "name": self.name
        }
