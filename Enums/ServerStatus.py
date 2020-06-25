from enum import Enum


class ServerStatus(Enum):
    Online = 1
    Restarting = 1
    Offline = 3
    StartingUp = 4
    WaitingForCamera = 5
    ErrorOccurred = 6

