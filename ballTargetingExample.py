import cv2

from imageProcessing import get_colored_objects
from transfer import Transfer
from params import SEND_MODE

vid = cv2.VideoCapture(1)

if SEND_MODE == 'usb':
    transferObj = Transfer()
    print(transferObj.get_dev())

if __name__ == '__main__':
    while True:

        ret, frame = vid.read()

        formattedFrame, data, coords, output, centers = get_colored_objects(
            frame, 
            color=['red'],
            num_items_each=-1
        )

        if SEND_MODE == 'print':
            print(data)
        elif SEND_MODE == 'usb':
            for entry in data:
                transferObj.send(entry)

        cv2.imshow('colorDetection', formattedFrame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    vid.release()

    cv2.destroyAllWindows()
