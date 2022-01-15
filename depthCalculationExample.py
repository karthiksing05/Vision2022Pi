import cv2

from stereoVision import StereoVision
from transfer import Transfer
from params import SEND_MODE

lVid = cv2.VideoCapture(0)
rVid = cv2.VideoCapture(1)
sv = StereoVision()

if SEND_MODE == 'usb':
    transferObj = Transfer()
    print(transferObj.get_dev())

if __name__ == '__main__':
    while True:

        ret, lFrame = lVid.read()
        ret, rFrame = rVid.read()
        formattedFrame, data = StereoVision.create_disparity(lFrame, rFrame)

        if SEND_MODE == 'print':
            print(data)
        elif SEND_MODE == 'usb':
            for entry in data:
                transferObj.send(entry)

        cv2.imshow('colorDetection', formattedFrame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    lVid.release()
    rVid.release()

    cv2.destroyAllWindows()
