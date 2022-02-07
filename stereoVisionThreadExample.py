import sys
import cv2
import numpy as np

# Functions for stereo vision
from stereoVisionUtils import add_HSV_filter as add_HSV_filter
from stereoVisionUtils import find_centers
from stereoVisionUtils import find_depth as tri
from stereoVisionUtils import calibrate

# Multithreading class!!!
from threadUtils import VideoGet, CountsPerSec

# My imports for constant parameters and the Transfer USB class
from params import *
from transfer import Transfer

# Open both cameras
cap_right = VideoGet(SRC_RIGHT).start() # cv2.VideoCapture(2)
cap_left =  VideoGet(SRC_LEFT).start() # cv2.VideoCapture(0)

cps = CountsPerSec().start()

# cap_right.set(cv2.CAP_PROP_BUFFERSIZE, BUFFER_SIZE)
# cap_left.set(cv2.CAP_PROP_BUFFERSIZE, BUFFER_SIZE)

if SEND_MODE == 'usb':
    transferObj = Transfer()
    print(transferObj.get_dev())

if __name__ == '__main__':
    while True:

        frame_right = cap_right.frame
        frame_left = cap_left.frame

        # If cannot catch any frame, break
        if cap_right.grabbed == False or cap_left.grabbed == False:                    
            continue

        ################## CALIBRATION #########################################################

        # frame_right, frame_left = calibrate(frame_right, frame_left)

        ########################################################################################

        cps.increment()

        scale_percent = 50 # percent of original size

        reWidthL = int(frame_left.shape[1] * scale_percent / 100)
        reHeightL = int(frame_left.shape[0] * scale_percent / 100)
        frame_left = cv2.resize(frame_left, (reWidthL, reHeightL))

        reWidthR = int(frame_right.shape[1] * scale_percent / 100)
        reHeightR = int(frame_right.shape[0] * scale_percent / 100)
        frame_right = cv2.resize(frame_right, (reWidthR, reHeightR))

        # APPLYING add_HSV_filter-FILTER:
        frame_right, mask_right = add_HSV_filter(frame_right, 1)
        frame_left, mask_left = add_HSV_filter(frame_left, 0)

        # APPLYING find_centers RECOGNITION:
        centers_right, offsetR = find_centers(frame_right, mask_right)
        centers_left, offsetL  = find_centers(frame_left, mask_left)

        offset = (((offsetL[0] + offsetR[0]) / 2), ((offsetL[1] + offsetR[1]) / 2))

        ################## CALCULATING BALL DEPTH #########################################################
        # """
        # continue looping
        if np.all(centers_right) == None or np.all(centers_left) == None:
            continue

        else:
            depth = tri(centers_right, centers_left, frame_right, frame_left, DIST_BTW_CAMS, FOCAL_LENGTH, FOV)
            depth = round(depth, 3)
            # Multiply computer value with a value to get real-life depth in [cm]. The factor was found manually.
            # cv2.putText(frame_right, "TRACKING", (75, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0),2)
            # cv2.putText(frame_left, "TRACKING", (75, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0),2)
            # cv2.putText(frame_right, "Distance: " + str(depth), (200,50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (124,252,0),2)
            # cv2.putText(frame_left, "Distance: " + str(depth), (200,50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (124,252,0),2)
            
            entry = {
                "depth":depth,
                "x-offset":offset[0],
                "y-offset":offset[1]
            }

            if SEND_MODE == 'print':
                print("Data: ", entry)
            elif SEND_MODE == 'usb':
                transferObj.send(entry)
        # """

        # Show the frames
        formattedFrameMask = np.hstack([mask_left, mask_right])
        cv2.imshow("Masks", formattedFrameMask)
        formattedFrameClean = np.hstack([frame_left, frame_right])
        cv2.imshow("Raw Images", formattedFrameClean)

        # Hit "q" to close the window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap_left.stop()
            cap_right.stop()
            break

        del frame_left
        del frame_right


    # Release and destroy all windows before termination
    cv2.destroyAllWindows()
