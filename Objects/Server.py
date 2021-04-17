class Server:
    def __init__(self):
        # Properties
        self.ServerID = 0
        self.Name = None
        self.MacAddress = None
        self.InternalAddress = None
        self.ExternalAddress = None
        self.PortNumber = None
        self.DirectoryPath = None
        self.ServerStatusID = None

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
                self.Name = value
                continue
            if "MacAddress" in key:
                self.MacAddress = value
                continue
            if "InternalAddress" in key:
                self.InternalAddress = value
                continue
            if "ExternalAddress" in key:
                self.ExternalAddress = value
                continue
            if "PortNumber" in key:
                self.PortNumber = value
                continue
            if "DirectoryPath" in key:
                self.DirectoryPath = value
                continue
            if "ServerStatusID" in key:
                self.ServerStatusID = value
                continue
