import datetime
from queue import Queue
import os
from vidgear.gears import NetGear
from BL import CameraBL, ServerBL
from MachineLearning.SingleMotionDetector import SingleMotionDetector
import cv2
from Helpers import VideoBuilderHelper, VideoCombinerHelper, VideoFeedRetrieverHelper
from Enums import ServerStatus


server = ServerBL.startup()
if server is None:
    ServerBL.attempt_repair()
else:
    print("Server Initialized!")

queues = []

# Get all cameras that are linked to this Server
cameras = CameraBL.get_all_cameras_for_server(server)
if len(cameras) > 0:
    # Create a new thread for every camera
    for camera in cameras:
        retriever_queue = Queue()
        video_retriever = VideoFeedRetrieverHelper.VideoRetriever(retriever_queue)
        video_retriever.daemon = True
        video_retriever.start()
        parameters = [camera, server]
        retriever_queue.put(parameters)
        queues.append(retriever_queue)
else:
    ServerBL.standby(server)

# We do not expect our queues to ever actually end
for thread in queues:
    thread.join()
