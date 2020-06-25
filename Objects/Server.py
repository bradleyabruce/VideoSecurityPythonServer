class Server:
    def __init__(self):
        # Properties
        self.ServerID = 0
        self.Name = None
        self.MacAddress = None
        self.InternalIPAddress = None
        self.ExternalIPAddress = None
        self.PortNumber = None
        self.DirectoryPath = None
        self.StatusID = None
        self.IsDebug = None

        # Unmapable Properties
        self.client = None
        self.md = None
        self.last_builder_queue = None
        # Directory Variables
        self.full_directory = None
        # Time Variables
        self.current_minute = None
        self.previous_minute = None

    def mapper(self, result_set):
        for key, value in result_set.items():
            if "ServerID" in key:
                self.ServerID = value
                continue
            if "Name" in key:
                self.Name = str(value)
                continue
            if "MacAddress" in key:
                self.MacAddress = str(value)
                continue
            if "InternalIPAddress" in key:
                self.InternalIPAddress = str(value)
                continue
            if "ExternalIPAddress" in key:
                self.ExternalIPAddress = value
                continue
            if "PortNumber" in key:
                self.PortNumber = str(value)
                continue
            if "DirectoryPath" in key:
                self.DirectoryPath = value
                continue
            if "StatusID" in key:
                self.StatusID = value
                continue
            if "IsDebug" in key:
                if value == 0 or value == 1:
                    self.IsDebug = bool(value)
                else:
                    self.IsDebug = False
                continue
