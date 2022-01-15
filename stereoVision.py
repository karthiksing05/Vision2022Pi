import cv2
import numpy as np

import matplotlib.pyplot as plt

from params import FLANN_INDEX_KDTREE

class StereoVision(object):
    def __init__(self):
        pass

    def _cap_rect_images(self, imgL, imgR):
        """
        Testing stereoRectification on double cameras
        any variable with the number 1 in it is used for left img and 2 is for right img
        """

        img1 = imgL
        img2 = imgR

        sift = cv2.SIFT_create()
        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(img1, None)
        kp2, des2 = sift.detectAndCompute(img2, None)

        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)   # or pass empty dictionary
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1, des2, k=2)

        matchesMask = [[0, 0] for i in range(len(matches))]
        good = []
        pts1 = []
        pts2 = []

        for i, (m, n) in enumerate(matches):
            if m.distance < 0.7*n.distance:
                # Keep this keypoint pair
                matchesMask[i] = [1, 0]
                good.append(m)
                pts2.append(kp2[m.trainIdx].pt)
                pts1.append(kp1[m.queryIdx].pt)

        pts1 = np.int32(pts1)
        pts2 = np.int32(pts2)
        fundamental_matrix, inliers = cv2.findFundamentalMat(pts1, pts2, cv2.FM_RANSAC)

        # We select only inlier points
        pts1 = pts1[inliers.ravel() == 1]
        pts2 = pts2[inliers.ravel() == 1]

        lines1 = cv2.computeCorrespondEpilines(
            pts2.reshape(-1, 1, 2), 2, fundamental_matrix)
        lines1 = lines1.reshape(-1, 3)

        lines2 = cv2.computeCorrespondEpilines(
            pts1.reshape(-1, 1, 2), 1, fundamental_matrix)
        lines2 = lines2.reshape(-1, 3)

        h1, w1 = img1.shape
        h2, w2 = img2.shape
        _, H1, H2 = cv2.stereoRectifyUncalibrated(
            np.float32(pts1), np.float32(pts2), fundamental_matrix, imgSize=(w1, h1)
        )

        img1_rectified = cv2.warpPerspective(img1, H1, (w1, h1))
        img2_rectified = cv2.warpPerspective(img2, H2, (w2, h2))
        # cv2.imwrite("rectified_1.png", img1_rectified)
        # cv2.imwrite("rectified_2.png", img2_rectified)

        return img1_rectified, img2_rectified


    def create_disparity(self):
        """
        This function creates a stereo vision object and shows a disparity graph

        Darker colors constitute farther away images
        """
        imgL, imgR = self._cap_rect_images()
        stereo = cv2.StereoBM_create(numDisparities=16, blockSize=15)
        disparity = stereo.compute(imgL, imgR)
        plt.imshow(disparity, 'gray')
        plt.show()

        return disparity
