import cv2


class CameraInfo:
    def __init__(self):
        # Initialize Camera variables
        self.frame_rate_calc = 1
        self.freq = cv2.getTickFrequency()
        self.font = cv2.FONT_HERSHEY_SIMPLEX

        # Initialize ml variables
        self.frames_before_detection = 15
        self.frame_count = 0

        self.image_array = []
        self.video_combiner_started = False
