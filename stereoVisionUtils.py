import sys
import cv2
import numpy as np
import imutils

from params import *

def add_HSV_filter(frame, camera):

	# Blurring the frame
    blur = cv2.GaussianBlur(frame,(5,5),0) 

    # Converting RGB to HSV
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    l_b_r = np.array(GREEN_BOUNDS[0])       # Lower limit for red ball
    u_b_r = np.array(GREEN_BOUNDS[1])       # Upper limit for red ball
    l_b_l = np.array(GREEN_BOUNDS[0])        # Lower limit for red ball
    u_b_l = np.array(GREEN_BOUNDS[1])       # Upper limit for red ball

    if (camera == 1):
        mask = cv2.inRange(hsv, l_b_r, u_b_r)
    else:
        mask = cv2.inRange(hsv, l_b_l, u_b_l)

    # Morphological Operation - Opening - Erode followed by Dilate - Remove noise
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    return frame, mask

def find_centers(frame, mask):

    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    frameH, frameW, _ = frame.shape
    frameCenter = (int(frameW / 2), int(frameH / 2))
    centerWidth = frameW / 2

    # Only proceed if at least one contour was found
    if len(contours) > 0:
        past_width = 0
        c = None
        for contour in contours:
            M = cv2.moments(contour)
            center_width = int(M["m10"] / M["m00"])
            if min((past_width, center_width), key=lambda x: abs((centerWidth) - x)) == center_width: # Look at this line
                x, y, w, h = cv2.boundingRect(contour)
                c = contour

        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
        cv2.drawMarker(frame, center, (0, 0, 0), cv2.MARKER_CROSS, 5, 2)

        offset = (frameCenter[0] - center[0], frameCenter[1] - center[1]) # x offset and y offset (in pixels)

        return center, offset

    return (0, 0)

def calibrate(frameR, frameL):

    # Load parameters attained from "calib_parameters.py"
    ret = np.load("./Calibration/camera_params/ret.npy")
    K = np.load("./Calibration/camera_params/K.npy")
    dist = np.load("./Calibration/camera_params/dist.npy")
    rvecs = np.load("./Calibration/camera_params/rvecs.npy")
    tvecs = np.load("./Calibration/camera_params/tvecs.npy")


    hR,wR = frameR.shape[:2]
    hL,wL = frameL.shape[:2]
    new_camera_matrixR, roiR = cv2.getOptimalNewCameraMatrix(K,dist,(wR,hR),1,(wR,hR))
    new_camera_matrixL, roiL = cv2.getOptimalNewCameraMatrix(K,dist,(wL,hL),1,(wL,hL))

    #Undistort images
    frame_undistortedR = cv2.undistort(frameR, K, dist, None, new_camera_matrixR)
    frame_undistortedL = cv2.undistort(frameL, K, dist, None, new_camera_matrixL)

    # Uncomment if you want help lines:
    # frame_undistortedR = cv2.line(frame_undistortedR, (0,int(hR/2)), (wR,240), (0, 255, 0) , 5)
    # frame_undistortedR = cv2.line(frame_undistortedR, (int(wR/2),0), (int(wR/2),hR), (0, 255, 0) , 5)
    # frame_undistortedL = cv2.line(frame_undistortedL, (int(wL/2),0), (int(wL/2),hL), (0, 255, 0) , 5)
    # frame_undistortedL = cv2.line(frame_undistortedL, (0,int(hL/2)), (wL,240), (0, 255, 0) , 5)
    # print(K)

    return frame_undistortedR, frame_undistortedL

def find_depth(circle_right, circle_left, frame_right, frame_left, baseline,f, alpha):

    # CONVERT FOCAL LENGTH f FROM [mm] TO [pixel]:
    height_right, width_right, depth_right = frame_right.shape
    height_left, width_left, depth_left = frame_left.shape

    if width_right == width_left:
        f_pixel = (width_right * 0.5) / np.tan(alpha * 0.5 * np.pi/180)

    else:
        print('Left and right camera frames do not have the same pixel width')

    x_right = circle_right[0]
    x_left = circle_left[0]

    # CALCULATE THE DISPARITY:
    disparity = x_left - x_right      #Displacement between left and right frames [pixels]

    # CALCULATE DEPTH z:
    zDepth = (baseline*f_pixel)/disparity             #Depth in [cm]

    return abs(zDepth)
