from enum import Enum


class ServerStatus(Enum):
    Offline = 1
    StartingUp = 2
    WaitingForCamera = 3
    ConnectedToCamera = 4
    Error = 5

