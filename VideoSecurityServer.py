import datetime
from queue import Queue
import os
from vidgear.gears import NetGear
from BL import CameraBL, ServerBL
from MachineLearning.SingleMotionDetector import SingleMotionDetector
import cv2
from Helpers import VideoBuilderHelper, VideoCombinerHelper, VideoRetrieverHelper


# Get Server info from database
print("Initializing Server...")
server = ServerBL.startup()
print("Server Initialized!")

queues = []

# Get all cameras that are linked to this Server
cameras = CameraBL.get_all_cameras(server)
if cameras is not None and len(cameras) > 0:
    # Create a new thread for every camera to run off of
    for camera in cameras:
        retriever_queue = Queue()
        video_retriever = VideoRetrieverHelper.VideoRetriever(retriever_queue)
        video_retriever.daemon = True
        video_retriever.start()
        parameters = [camera, server]
        retriever_queue.put(parameters)
        queues.append(retriever_queue)
else:
    print("No Cameras")

# We do not expect our queues to ever actually end
for thread in queues:
    thread.join()

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

def combine_videos(self):
    # We need to wait until the hour is done before combining videos
    if self.last_builder_queue.unfinished_tasks == 0:
        video_hour = (datetime.datetime.now() + datetime.timedelta(hours=-1)).hour
        full_directory = self.day_directory + "/" + str(video_hour)

        combiner_queue = Queue()
        video_combiner = VideoCombinerHelper.VideoCombiner(combiner_queue)
        video_combiner.daemon = True
        video_combiner.start()
        combiner_queue.put(full_directory)

        # After we have begun the combine process, set the builder queue to None
        self.last_builder_queue = None

def create_video(self):
    # Create new video
    builder_queue = Queue()
    video_builder = VideoBuilderHelper.VideoBuilder(builder_queue)
    video_builder.daemon = True
    video_builder.start()
    builder_queue.put((self.camera_info.image_array.copy(), self.day_directory))

    # Save the builder_queue at the end of every hour
    if self.current_minute == 0:
        self.last_builder_queue = builder_queue
        print("Builder queue saved.")

    self.camera_info.image_array.clear()

def run(self):
    self.previous_minute = self.get_minute()
    # Continue to retrieve frames from the client as long as it is broadcasting
    while True:
        # Check time
        self.current_minute = self.get_minute()
        self.build_current_day_directory()

        if self.last_builder_queue is not None:
            self.combine_videos()

        if self.current_minute != self.previous_minute:
            # Every minute, create a video for us
            self.create_video()

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

            # Allow the loop to continue
            self.previous_minute = self.current_minute

        if cv2.waitKey(1) == ord('q'):
            break

    # safely close objects
    self.client.close()
    cv2.destroyAllWindows()
