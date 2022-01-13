import cv2
import numpy as np

class StereoVision(object):
    def __init__(lCam=1, rCam=2):
        self.lCam = cv2.VideoCapture(lCam)
        self.rCam = cv2.VideoCapture(lCam)

    def _cap_rect_images():
        """
        Applying stereo image rectification on the images
        """
        retL, imgL = self.lCam.read()
        retR, imgR = self.rCam.read()

        rectL = cv2.remap(imgL_gray,
							Left_Stereo_Map_x,
							Left_Stereo_Map_y,
							cv2.INTER_LANCZOS4,
							cv2.BORDER_CONSTANT,
							0)
		
		rectR = cv2.remap(imgR_gray,
							Right_Stereo_Map_x,
							Right_Stereo_Map_y,
							cv2.INTER_LANCZOS4,
							cv2.BORDER_CONSTANT,
							0)

        return rectL, rectR

    def create_stereo():
        """
        This function creates a stereo vision object and shows a disparity graph

        Darker colors constitute farther away images
        """
        imgL, imgR = _cap_images()
        stereo = cv.StereoBM_create(numDisparities=16, blockSize=15)
        disparity = stereo.compute(imgL, imgR)
        plt.imshow(disparity, 'gray')
        plt.show()
