import os
from datetime import datetime, timedelta
from threading import Thread
from time import time
import cv2
import gc


def create_hour_directory(day_directory, video_hour):
    full_directory = os.getcwd() + "/" + day_directory + "/" + str(video_hour)
    if not os.path.exists(full_directory):
        os.makedirs(full_directory)
    return full_directory


def get_hour(timestamp):
    if timestamp.minute == 0:
        return (timestamp + timedelta(hours=-1)).hour
    else:
        return timestamp.hour


def get_file_name(timestamp):
    previous_min = timestamp + timedelta(minutes=-1)
    return str(previous_min.minute) + ".mp4"


def build_video(image_array, day_directory):
    # Time stamp info
    timestamp = datetime.now()

    # We need to put the videos in the correct directory based on hour
    video_hour = get_hour(timestamp)
    full_directory = create_hour_directory(day_directory, video_hour)

    print("-------------------------------------------")
    print("Generating video for " + timestamp.strftime("%b %d %Y %H %M"))
    print("Total frames to splice: " + str(len(image_array) - 1))

    # Stopwatch
    start = time()

    # image properties
    img = image_array[0]
    height, width, layers = img.shape
    size = (width, height)

    file_name = get_file_name(timestamp)

    out = cv2.VideoWriter(full_directory + "/" + file_name, cv2.VideoWriter_fourcc(*'DIVX'), 15, size)
    for i in range(len(image_array)):
        out.write(image_array[i])
    out.release()

    # Clear unneeded variables
    image_array.clear()
    # Stop stopwatch
    end = time()

    print("Video complete")
    print("Elapsed Time: " + str(end - start))
    print("-------------------------------------------")
    gc.collect()


class VideoBuilder(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            image_array, day_directory = self.queue.get()
            try:
                build_video(image_array, day_directory)
            finally:
                self.queue.task_done()

