import cv2


class Camera:
    def __init__(self):
        # Mapable Properties
        self.CameraID = 0
        self.Name = None
        self.MacAddress = None
        self.InternalIPAddress = None
        self.ExternalIPAddress = None
        self.Height = None
        self.Width = None
        self.DirectoryPath = None
        self.StatusID = None

        # Unmapable Properties
        self.frame_rate_calc = 1
        self.freq = cv2.getTickFrequency()
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        # Machine Learning Properties
        self.frames_before_detection = 15
        self.frame_count = 0
        # video generation Properties
        self.image_array = []
        self.video_combiner_started = False

    def mapper(self, result_set):
        for key, value in result_set.items():
            if "CameraID" in key:
                self.CameraID = value
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
            if "Height" in key:
                self.Height = value
                continue
            if "Width" in key:
                self.Width = value
                continue
            if "DirectoryPath" in key:
                self.DirectoryPath = value
                continue
            if "StatusID" in key:
                self.StatusID = value
                continue
