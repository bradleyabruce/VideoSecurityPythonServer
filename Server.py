import datetime
from queue import Queue
import os
from vidgear.gears import NetGear
from BL.CameraInfo import CameraInfo
from MachineLearning.SingleMotionDetector import SingleMotionDetector
import cv2
from VideoHelpers import VideoBuilder, VideoCombiner


class Server:
    def __init__(self):
        # Determine debug mode
        self.IS_DEBUG = False
        self.camera_info = CameraInfo()
        self.client = NetGear(address='192.168.1.34', port='8089', receive_mode=True, protocol='tcp')
        self.md = SingleMotionDetector(accumWeight=0.1)

        # Directory Variables
        self.day_directory = None

        # Time Variables
        self.start_minute = None
        self.minutes_saved = []

    # Machine Learning Method
    def detect_motion(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)
        if self.camera_info.frame_count > self.camera_info.frames_before_detection:
            # detect motion in the image
            motion = self.md.detect(gray)
            # check to see if motion was found in the frame
            if motion is not None:
                # unpack the tuple and draw the box surrounding the
                # "motion area" on the output frame
                (thresh, (minX, minY, maxX, maxY)) = motion
                cv2.rectangle(image, (minX, minY), (maxX, maxY),
                              (0, 0, 255), 2)

        # update the background model and return final frame
        self.md.update(gray)
        return image

    def draw_camera_info(self, image):
        # grab the current timestamp and draw it on the frame
        timestamp = datetime.datetime.now()
        cv2.putText(image, timestamp.strftime("%A %d %B %Y %I:%M:%S%p"), (8, 25), self.camera_info.font, .7, (0, 0, 0),
                    2,
                    cv2.LINE_AA)
        cv2.putText(image, timestamp.strftime("%A %d %B %Y %I:%M:%S%p"), (8, 25), self.camera_info.font, .7,
                    (255, 255, 255), 1,
                    cv2.LINE_AA)

        # Show frame rate
        cv2.putText(image, "FPS: {0:.2f}".format(self.camera_info.frame_rate_calc), (8, 55), self.camera_info.font, .7, (0, 0, 0),
                    2,
                    cv2.LINE_AA)
        cv2.putText(image, "FPS: {0:.2f}".format(self.camera_info.frame_rate_calc), (8, 55), self.camera_info.font, .7,
                    (255, 255, 255), 1,
                    cv2.LINE_AA)
        return image

    def build_current_day_directory(self):
        directory_name = "Videos/" + datetime.datetime.now().strftime("%m %d %Y")
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)
        self.day_directory = directory_name

    @staticmethod
    def get_minute():
        return datetime.datetime.now().minute

    def combine_videos_if_needed(self, current_minute):
        if current_minute == 0 and self.day_directory is not None:
            combiner_queue = Queue()
            video_combiner = VideoCombiner.VideoCombiner(combiner_queue)
            video_combiner.daemon = True
            video_combiner.start()
            combiner_queue.put((self.day_directory, current_minute))

    def clear_minutes_saved_if_needed(self, current_minute):
        if current_minute == self.start_minute and (len(self.minutes_saved) > 2):
            print("Clearing saved minutes with start minute " + str(self.start_minute) + " at current minute: " + str(
                current_minute))
            self.minutes_saved.clear()

    def create_video_if_needed(self, current_minute):
        if current_minute not in self.minutes_saved and current_minute % 5 == 0:
            # Create new video
            if self.camera_info.frame_count != 0:
                builder_queue = Queue()
                video_builder = VideoBuilder.VideoBuilder(builder_queue)
                video_builder.daemon = True
                video_builder.start()
                builder_queue.put((self.camera_info.image_array.copy(), self.day_directory))

                self.camera_info.image_array.clear()
                self.minutes_saved.append(current_minute)

    def run(self):
        # Initialize start time
        self.start_minute = self.get_minute()

        # Continue to retrieve frames from the client as long as it is broadcasting
        while True:
            # Check time
            current_minute = datetime.datetime.now().minute

            # self.combine_videos_if_needed(current_minute)

            # This will only create directory every night at midnight
            self.build_current_day_directory()

            # Allow for infinite loop of creating videos
            self.clear_minutes_saved_if_needed(current_minute)

            # We need to stop a video from being created if we start at a 5 minute interval of time
            if current_minute % 5 == 0 and self.camera_info.frame_count == 0:
                self.minutes_saved.append(current_minute)

            # Every five minutes, create a video for us
            self.create_video_if_needed(current_minute)

            t1 = cv2.getTickCount()
            # Get frame from client
            frame = self.client.recv()
            self.camera_info.frame_count += 1

            if self.camera_info.frame_count == 1:
                print("Stream Connected.")

            if frame is None:
                print("Image received was null.")
                break
            else:
                frame = self.detect_motion(frame)
                frame = self.draw_camera_info(frame)

                # Save image for video
                self.camera_info.image_array.append(frame)

                # Show frame (for testing purposes)
                if self.IS_DEBUG:
                    ims = cv2.resize(frame, (960, 540))  # Resize image
                    cv2.imshow("output", ims)

                # FPS Calculation
                t2 = cv2.getTickCount()
                time1 = (t2 - t1) / self.camera_info.freq
                self.camera_info.frame_rate_calc = 1 / time1

            if cv2.waitKey(1) == ord('q'):
                break

        # safely close objects
        self.client.close()
        cv2.destroyAllWindows()


server = Server()
server.run()
