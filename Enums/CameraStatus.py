from enum import Enum


class CameraStatus(Enum):
    Online = 1
    Restarting = 1
    Offline = 3
    StartingUp = 4
    WaitingForServer = 5
    ErrorOccurred = 6

