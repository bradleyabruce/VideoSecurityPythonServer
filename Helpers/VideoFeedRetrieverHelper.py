import errno
import os
import random
import signal
from contextlib import contextmanager
from datetime import datetime, timedelta
from queue import Queue
from threading import Thread
import cv2
from termcolor import colored
from vidgear.gears import NetGear

from Helpers import VideoCombinerHelper, VideoBuilderHelper
from MachineLearning.SingleMotionDetector import SingleMotionDetector


class VideoRetriever(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue
        self.camera = None
        self.server = None
        self.color = None

    def run(self):
        while True:
            parameters = self.queue.get()
            try:
                self.camera = parameters[0]
                self.server = parameters[1]
                self.retrieve_video()
            finally:
                self.queue.task_done()


    # TODO AccumWeight can be added to tCamera
    def retrieve_video(self):
        self.color = self.get_random_color()
        try:
            print(colored("Camera " + str(self.camera.CameraID) + ": New thread started on current server.", self.color))
            netgear = self.create_netgear()

            self.camera.motion_detector = SingleMotionDetector(accumWeight=0.6)

            first_frame = netgear.recv()
            if first_frame is not None:
                print(colored("Camera " + str(self.camera.CameraID) + ": Connected!", self.color))
                print(colored("Camera " + str(self.camera.CameraID) + ": Recording camera feed.", self.color))

            self.server.previous_minute = self.get_minute()
            self.server.current_minute = None
            while True:
                # Check time
                self.server.current_minute = self.get_minute()

                self.build_current_day_directory()

                if self.camera.last_builder_queue is not None:
                    self.combine_videos()

                if self.server.current_minute != self.server.previous_minute:
                    # Every minute, create a video for us
                    self.create_video()

                t1 = cv2.getTickCount()
                # Get frame from client
                frame = netgear.recv()
                self.camera.frame_count += 1
                # TODO None check

                frame = self.detect_motion(frame)
                frame = self.draw_camera_info(frame)

                # Save image for video
                self.camera.image_array.append(frame)

                # Show frame (for testing purposes)
                # if server.IsDebug:
                #if True:
                #    ims = cv2.resize(frame, (960, 540))  # Resize image
                #    cv2.imshow("output", ims)

                # FPS Calculation
                t2 = cv2.getTickCount()
                time1 = (t2 - t1) / self.camera.freq
                self.camera.frame_rate_calc = 1 / time1

                # Allow the loop to continue
                self.server.previous_minute = self.server.current_minute

                if cv2.waitKey(1) == ord('q'):
                    break

            # safely close objects
            netgear.close()
            cv2.destroyAllWindows()

        except Exception as exc:
            print(colored("Camera " + str(self.camera.CameraID) + ": Error Occurred - " + str(exc), self.color))
            # Change camera status

    def build_current_day_directory(self):
        directory_name = "Videos/" + self.server.DirectoryPath + self.camera.DirectoryPath + datetime.now().strftime("%m %d %Y")
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)
        self.server.full_directory = directory_name

    def combine_videos(self):
        # We need to wait until the hour is done before combining videos
        if self.camera.last_builder_queue.unfinished_tasks == 0:
            video_hour = (datetime.now() + timedelta(hours=-1)).hour
            full_directory = self.server.full_directory + "/" + str(video_hour)

            combiner_queue = Queue()
            video_combiner = VideoCombinerHelper.VideoCombiner(combiner_queue)
            video_combiner.daemon = True
            video_combiner.start()
            combiner_queue.put(full_directory)

            # After we have begun the combine process, set the builder queue to None
            self.camera.last_builder_queue = None

    def create_video(self):
        # Create new video
        builder_queue = Queue()
        video_builder = VideoBuilderHelper.VideoBuilder(builder_queue)
        video_builder.daemon = True
        video_builder.start()
        builder_queue.put((self.camera.image_array.copy(), self.server.full_directory))

        # Save the builder_queue at the end of every hour
        if self.server.current_minute == 0:
            self.camera.last_builder_queue = builder_queue
            print("Builder queue saved.")

        self.camera.image_array.clear()

    def draw_camera_info(self, image):
        # grab the current timestamp and draw it on the frame
        timestamp = datetime.now()
        cv2.putText(image, timestamp.strftime("%A %d %B %Y %I:%M:%S%p"), (8, 25), self.camera.font, .7, (0, 0, 0),
                    2,
                    cv2.LINE_AA)
        cv2.putText(image, timestamp.strftime("%A %d %B %Y %I:%M:%S%p"), (8, 25), self.camera.font, .7,
                    (255, 255, 255), 1,
                    cv2.LINE_AA)

        # Show frame rate
        cv2.putText(image, "FPS: {0:.2f}".format(self.camera.frame_rate_calc), (8, 55), self.camera.font, .7, (0, 0, 0),
                    2,
                    cv2.LINE_AA)
        cv2.putText(image, "FPS: {0:.2f}".format(self.camera.frame_rate_calc), (8, 55), self.camera.font, .7,
                    (255, 255, 255), 1,
                    cv2.LINE_AA)
        return image

    # Machine Learning Method
    def detect_motion(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)
        if self.camera.frame_count > self.camera.frames_before_detection:
            # detect motion in the image
            motion = self.camera.motion_detector.detect(gray)
            # check to see if motion was found in the frame
            if motion is not None:
                # unpack the tuple and draw the box surrounding the
                # "motion area" on the output frame
                (thresh, (minX, minY, maxX, maxY)) = motion
                cv2.rectangle(image, (minX, minY), (maxX, maxY),
                              (0, 0, 255), 2)

        # update the background model and return final frame
        self.camera.motion_detector.update(gray)
        return image

    @staticmethod
    def get_minute():
        return datetime.now().minute

    def create_netgear(self):
        options = {'compression_param': cv2.IMREAD_COLOR}
        netgear = NetGear(address=self.server.InternalIPAddress, port=self.server.PortNumber, receive_mode=True, protocol='tcp',
                          **options)
        print(colored("Camera " + str(self.camera.CameraID) + ": Netgear established.", self.color))
        print(colored("Camera " + str(self.camera.CameraID) + ": Listening for connection...", self.color))
        return netgear

    @staticmethod
    def get_random_color():
        color_options = ["red", "green", "yellow", "blue", "magenta", "cyan"]
        return random.choice(color_options)