import os
from datetime import datetime, timedelta
from threading import Thread
from moviepy.editor import *
import natsort


def get_value_to_ignore(minute_to_ignore):
    if minute_to_ignore != 0:
        return str(minute_to_ignore - 5) + "-" + str(minute_to_ignore)
    else:
        return "55-0"


def combine_videos(directory, minute_to_ignore):
    # This method will run every single hour at minute 0

    # We have to ignore the video that is currently being created
    value_to_ignore = get_value_to_ignore(minute_to_ignore)

    video_hour = (datetime.now() + timedelta(hours=-1)).hour



    # Grab all of the available videos from the directory
    video_files = []
    video_file_paths = natsort.natsorted(os.listdir(directory))
    for file in video_file_paths:
        if file.endswith(".mp4") and value_to_ignore not in file and str(video_hour) in file:
            full_file_path = os.getcwd() + "/" + directory + "/" + file
            video = VideoFileClip(full_file_path, audio=False)
            video_files.append(video)

    if len(video_files) > 1:
        # create new directory for hour
        new_video_path = os.getcwd() + "/" + directory + "/" + str(video_hour)
        if not os.path.exists(new_video_path):
            os.makedirs(new_video_path)
        final_clip = concatenate_videoclips(video_files, method="compose")
        final_clip.write_videofile(new_video_path + "/video.mp4")

        # Remove extra videos
        for file in video_file_paths:
            if file.endswith(".mp4") and value_to_ignore not in file:
                full_file_path = os.getcwd() + "/" + directory + "/" + file
                os.remove(full_file_path)


class VideoCombiner(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            directory, minute_to_ignore = self.queue.get()
            try:
                combine_videos(directory, minute_to_ignore)
            finally:
                self.queue.task_done()