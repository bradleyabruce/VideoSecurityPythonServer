import random
from threading import Thread

import cv2
from termcolor import colored
from vidgear.gears import NetGear
from MachineLearning.SingleMotionDetector import SingleMotionDetector


# Port can be added to tServer
# AccumWeight can be added to tCamera

def retrieve_video(camera, server):
    color = get_random_color()
    print(colored("Camera " + str(camera.CameraID) + ": New thread started on current server.", color))

    options = {'compression_param': cv2.IMREAD_COLOR}
    netgear = NetGear(address=server.InternalIPAddress, port='8089', receive_mode=True, protocol='tcp', **options)
    print(colored("Camera " + str(camera.CameraID) + ": Netgear established.", color))
    print(colored("Camera " + str(camera.CameraID) + ": Listening for connection...", color))

    md = SingleMotionDetector(accumWeight=0.6)
    last_builder_queue = None


def get_random_color():
    color_options = ["red", "green", "yellow", "blue", "magenta", "cyan"]
    return random.choice(color_options)


class VideoRetriever(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            parameters = self.queue.get()
            try:
                camera = parameters[0]
                server = parameters[1]
                retrieve_video(camera, server)
            finally:
                self.queue.task_done()