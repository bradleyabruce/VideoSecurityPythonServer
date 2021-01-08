from enum import Enum


class ServerStatus(Enum):
    Offline = 1
    StartingUp = 2
    WaitingForExistingCamera = 3
    WaitingForNewCamera = 4
    ConnectedToCamera = 5
    Error = 6


