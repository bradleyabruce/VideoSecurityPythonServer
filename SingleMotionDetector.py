import cv2
import imutils
import numpy as np


# This class accepts an optional argument of accumWeight.
# The larger the accumWeight, the less the background will be factored in when accumulating the average weight
# The smaller the accumWeight, the more the background will be factored
class SingleMotionDetector:
    def __init__(self, accumWeight=0.5):
        # store accumulated weight factor
        self.accumWeight = accumWeight

        # initialize background model
        self.bg = None

    def update(self, image):
        # if background model is None, initalize it
        if self.bg is None:
            self.bg = image.copy().astype("float")
            return

        # update the background model by accumulating the weighted average
        cv2.accumulateWeighted(image, self.bg, self.accumWeight)

    def detect(self, image, tVal=25):
        # compute absolute difference between background model and new image passed then threshold the image delta
        delta = cv2.absdiff(self.bg.astype("uint8"), image)
        thresh = cv2.threshold(delta, tVal, 255, cv2.THRESH_BINARY)[1]

        # perform series of erosions and dilations to remove small blobs
        thresh = cv2.erode(thresh, None, iterations=2)
        thresh = cv2.dilate(thresh, None, iterations=2)

        # find contours in the thresholded image and initialize the min and max bounding box regions for motion
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        (minX, minY) = (np.inf, np.inf)
        (maxX, maxY) = (-np.inf, -np.inf)

        # if no contours are found, return None
        if len(cnts) == 0:
            return None

        # Otherwise, loop over contours
        for c in cnts:
            # compute bounding box and use it to update min and max bounding box regions
            (x, y, w, h) = cv2.boundingRect(c)
            (minX, minY) = (min(minX, x), min(minY, y))
            (maxX, maxY) = (max(maxX, x + w), max(maxY, y + h))

        # Otherwise, return a tuple of the threshold image along with bounding box
        return(thresh, (minX, minY, maxX, maxY))
