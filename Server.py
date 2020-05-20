import datetime
from queue import Queue
import os
from vidgear.gears import NetGear
from SingleMotionDetector import SingleMotionDetector
import cv2
import VideoBuilder
import VideoCombiner
import timedelta


class Server:
    def __init__(self):
        # Determine debug mode
        self.IS_DEBUG = False

        # Initialize Camera variables
        self.frame_rate_calc = 1
        self.freq = cv2.getTickFrequency()
        self.font = cv2.FONT_HERSHEY_SIMPLEX

        # Initialize the client that we will be connecting to
        self.client = NetGear(address='192.168.1.30', port='8089', receive_mode=True, protocol='tcp')

        # Initialize ml variables
        self.frames_before_detection = 15
        self.frame_count = 0
        self.md = SingleMotionDetector(accumWeight=0.1)

        # Directory Variables
        self.current_directory = None

        # Time Variables
        self.start_minute = None
        self.minutes_saved = []
        self.image_array = []
        self.video_combiner_started = False

    # Machine Learning Method
    def detect_motion(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)
        if self.frame_count > self.frames_before_detection:
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
        cv2.putText(image, timestamp.strftime("%A %d %B %Y %I:%M:%S%p"), (8, 25), self.font, .7, (0, 0, 0), 2,
                    cv2.LINE_AA)
        cv2.putText(image, timestamp.strftime("%A %d %B %Y %I:%M:%S%p"), (8, 25), self.font, .7, (255, 255, 255), 1,
                    cv2.LINE_AA)

        # Show frame rate
        cv2.putText(image, "FPS: {0:.2f}".format(self.frame_rate_calc), (8, 55), self.font, .7, (0, 0, 0), 2,
                    cv2.LINE_AA)
        cv2.putText(image, "FPS: {0:.2f}".format(self.frame_rate_calc), (8, 55), self.font, .7, (255, 255, 255), 1,
                    cv2.LINE_AA)
        return image

    def build_current_day_directory(self):
        directory_name = "Videos/" + datetime.datetime.now().strftime("%m %d %Y")
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)
        self.current_directory = directory_name

    def server_run(self):
        # Initialize start time
        self.start_minute = datetime.datetime.now().minute

        # Continue to retrieve frames from the client as long as it is broadcasting
        while True:
            # Check time
            current_minute = datetime.datetime.now().minute

            # Before getting the new directory, we need to check to see if we need to combine previous videos
            if current_minute == 40 and self.video_combiner_started is False and self.current_directory is not None:
                self.video_combiner_started = True
                combinerQueue = Queue()
                videoCombiner = VideoCombiner.VideoCombiner(combinerQueue)
                videoCombiner.daemon = True
                videoCombiner.start()
                combinerQueue.put((self.current_directory, current_minute))

            # Build new directory
            self.build_current_day_directory()

            # Allow for infinite loop of creating videos
            if current_minute == self.start_minute and (len(self.minutes_saved) > 2):
                print(
                    "Clearing saved minutes with start minute " + str(self.start_minute) + " at current minute: " + str(
                        current_minute))
                self.minutes_saved.clear()
                # We need to stop a video from being created if we start at a 5 minute interval of time
            if current_minute % 5 == 0 and self.frame_count == 0:
                self.minutes_saved.append(current_minute)
            # Every five minutes, create a video for us
            if current_minute not in self.minutes_saved and current_minute % 5 == 0:
                # Create new video
                if self.frame_count != 0:
                    queue = Queue()
                    videoBuilder = VideoBuilder.VideoBuilder(queue)
                    videoBuilder.daemon = True
                    videoBuilder.start()
                    queue.put((self.image_array.copy(), self.current_directory))

                    self.image_array.clear()
                    self.minutes_saved.append(current_minute)

            t1 = cv2.getTickCount()

            # Get frame from client
            frame = self.client.recv()
            self.frame_count += 1

            if self.frame_count == 1:
                print("Stream Connected.")

            if frame is None:
                print("Image received was null.")
                break
            else:
                frame = self.detect_motion(frame)
                frame = self.draw_camera_info(frame)

                # Save image for video
                self.image_array.append(frame)

                # Show frame (for testing purposes)
                if self.IS_DEBUG:
                    imS = cv2.resize(frame, (960, 540))  # Resize image
                    cv2.imshow("output", imS)

                # FPS Calculation
                t2 = cv2.getTickCount()
                time1 = (t2 - t1) / self.freq
                self.frame_rate_calc = 1 / time1

            if cv2.waitKey(1) == ord('q'):
                break

        # safely close objects
        self.client.close()
        cv2.destroyAllWindows()


server = Server()
server.server_run()
