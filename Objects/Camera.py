import cv2


class Camera:
    def __init__(self):
        # Mapable Properties
        self.CameraID = 0
        self.Name = None
        self.MacAddress = None
        self.InternalAddress = None
        self.ExternalAddress = None
        self.PortNumber = None
        self.StatusID = None
        self.DirectoryPath = None

        #
        # # Unmapable Properties
        # self.frame_rate_calc = 1
        # self.freq = cv2.getTickFrequency()
        # self.font = cv2.FONT_HERSHEY_SIMPLEX
        # # Machine Learning Properties
        # self.frames_before_detection = 15
        # self.frame_count = 0
        # self.motion_detector = None
        # # video generation Properties
        # self.image_array = []
        # self.video_combiner_started = False
        # self.last_builder_queue = None

    def mapper(self, result_set):
        for key in result_set:
            if "CameraID" in key:
                self.CameraID = result_set.get(key)[0]
                continue
            if "Name" in key:
                self.Name = result_set.get(key)[0]
                continue
            if "MacAddress" in key:
                self.MacAddress = result_set.get(key)[0]
                continue
            if "InternalIPAddress" in key:
                self.InternalAddress = result_set.get(key)[0]
                continue
            if "ExternalIPAddress" in key:
                self.ExternalAddress = result_set.get(key)[0]
                continue
            if "PortNumber" in key:
                self.PortNumber = result_set.get(key)[0]
                continue
            if "DirectoryPath" in key:
                self.DirectoryPath = result_set.get(key)[0]
                continue
            if "CameraStatusID" in key:
                self.StatusID = result_set.get(key)[0]
                continue
