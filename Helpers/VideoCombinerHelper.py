import os
from datetime import datetime, timedelta
from threading import Thread
from moviepy.editor import *
import natsort


# This method will run every single hour after all the videos have been created for that hour
def combine_videos(hour_directory):
    # Grab all of the available videos from the directory
    video_files = []
    full_directory = os.getcwd() + "/" + hour_directory
    for file in os.listdir(full_directory):
        if file.endswith(".mp4"):
            full_file_path = full_directory + "/" + file
            video = VideoFileClip(full_file_path, audio=False)
            video_files.append(video)

    if len(video_files) > 1:
        final_clip = concatenate_videoclips(video_files, method="compose")
        final_clip.write_videofile(full_directory + "/video.mp4")

        # Remove original videos
        for file in os.listdir(full_directory):
            if file.endswith(".mp4") and "video.mp4" not in file:
                file_path_to_remove = full_directory + "/" + file
                os.remove(file_path_to_remove)


class VideoCombiner(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            hour_directory = self.queue.get()
            try:
                combine_videos(hour_directory)
            finally:
                self.queue.task_done()
