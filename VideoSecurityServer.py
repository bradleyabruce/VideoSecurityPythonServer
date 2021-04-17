import time
from datetime import datetime
from queue import Queue
from BL import CameraBL, ServerBL
from Helpers import VideoFeedRetrieverHelper
from Enums.ServerStatus import ServerStatus

# Start server
print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " - Initializing server.")
server = ServerBL.startup()
if server is None:
    ServerBL.update_server_status(None, ServerStatus.Error.value, "Could not initialize server.")
    print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " - Could not initialize server.")
    quit()
else:
    ServerBL.update_server_status(server.ServerID, ServerStatus.ServerBootComplete.value, "Startup Complete.")
    print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " - Server Initialized.")


# Get currently linked cameras
queues = []
cameras = []
count = 1
ServerBL.update_server_status(server.ServerID, ServerStatus.ConnectingToCameraStart.value, "Connecting to camera.")

while len(cameras) == 0:
    print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " - Attempt (" + str(count) + ") to connect to camera ")
    cameras = CameraBL.get_all_cameras_for_server(server)
    count += 1
    time.sleep(10)

# Begin connecting to linked camera
print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " - Connecting to camera.")
for camera in cameras:
    retriever_queue = Queue()
    video_retriever = VideoFeedRetrieverHelper.VideoRetriever(retriever_queue)
    video_retriever.daemon = True
    video_retriever.start()
    parameters = [camera, server]
    retriever_queue.put(parameters)
    queues.append(retriever_queue)


# We do not expect our queues to ever actually end
for thread in queues:
    thread.join()
