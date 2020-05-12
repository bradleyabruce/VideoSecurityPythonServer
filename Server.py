import datetime
from vidgear.gears import NetGear
from vidgear.gears import WriteGear
import cv2
from SingleMotionDetector import SingleMotionDetector

# Determine debug mode
IS_DEBUG = True

# Initialize the client that we will be connecting to
client = NetGear(address='192.168.1.49', port='8089', receive_mode=True, protocol='tcp')
writer = WriteGear(output_filename='Output.mp4')

# Initialize ml variables
frame_number = 0
frame_count = 32
md = SingleMotionDetector(accumWeight=0.1)


def detect_motion(image, frames_passed):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 0)
    # grab the current timestamp and draw it on the frame
    timestamp = datetime.datetime.now()
    cv2.putText(image, timestamp.strftime(
        "%A %d %B %Y %I:%M:%S%p"), (10, image.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
    if frames_passed > frame_count:
        # detect motion in the image
        motion = md.detect(gray)
        # check to see if motion was found in the frame
        if motion is not None:
            # unpack the tuple and draw the box surrounding the
            # "motion area" on the output frame
            (thresh, (minX, minY, maxX, maxY)) = motion
            cv2.rectangle(frame, (minX, minY), (maxX, maxY),
                          (0, 0, 255), 2)

    # update the background model and return final frame
    md.update(gray)
    return image.copy()


# Continue to retrieve frames from the client as long as it is broadcasting
while True:
    frame_number += 1
    frame = client.recv()

    if frame is None:
        break;
    else:
        # Perform processing on frames
        frame = detect_motion(frame, frame_number)

        # Save Video
        writer.write(frame)

        # Show frame (for testing purposes)
        imS = cv2.resize(frame, (960, 540))  # Resize image
        cv2.imshow("output", imS)

    if cv2.waitKey(1) == ord('q'):
        break

# safely close objects
client.close()
writer.close()
cv2.destroyAllWindows()
