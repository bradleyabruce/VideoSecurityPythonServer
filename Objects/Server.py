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
        self.StatusID = None

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
        for key in result_set:
            if "ServerID" in key:
                self.ServerID = result_set.get(key)[0]
                continue
            if "Name" in key:
                self.Name = result_set.get(key)[0]
                continue
            if "MacAddress" in key:
                self.MacAddress = result_set.get(key)[0]
                continue
            if "InternalAddress" in key:
                self.InternalAddress = result_set.get(key)[0]
                continue
            if "ExternalAddress" in key:
                self.ExternalAddress = result_set.get(key)[0]
                continue
            if "PortNumber" in key:
                self.PortNumber = result_set.get(key)[0]
                continue
            if "DirectoryPath" in key:
                self.DirectoryPath = result_set.get(key)[0]
                continue
            if "StatusID" in key:
                self.StatusID = result_set.get(key)[0]
                continue
