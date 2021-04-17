from enum import Enum


class ServerStatus(Enum):
    Offline = 1
    ServerBootStart = 2
    ServerBootComplete = 3
    ConnectingToCameraStart = 4
    ConnectingToCameraComplete = 5
    Recording = 6
    Error = 7


