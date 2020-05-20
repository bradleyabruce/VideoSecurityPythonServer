from datetime import datetime
from threading import Thread
from time import time
import cv2
import gc


def build_video(image_array, directory):
    # Time stamp info
    timestamp = datetime.now()
    print("-------------------------------------------")
    print("Generating video for " + timestamp.strftime("%b %d %Y %H %M"))
    print("Total frames to splice: " + str(len(image_array) - 1))

    # Stopwatch
    start = time()

    # image properties
    img = image_array[0]
    height, width, layers = img.shape
    size = (width, height)

    # time properties
    video_start_minute = timestamp.minute - 5
    video_end_minute = timestamp.minute
    if video_end_minute == 0:
        video_start_minute = 55
    file_name = timestamp.strftime("%H ") + str(video_start_minute) + "-" + str(video_end_minute) + ".mp4"

    out = cv2.VideoWriter(directory + "/" + file_name, cv2.VideoWriter_fourcc(*'DIVX'), 15, size)
    for i in range(len(image_array)):
        out.write(image_array[i])
    out.release()

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
            image_array, directory = self.queue.get()
            try:
                build_video(image_array, directory)
            finally:
                self.queue.task_done()

