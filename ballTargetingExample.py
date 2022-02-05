import cv2
from fastCam import Camera

from imageProcessing import get_colored_objects
from transfer import Transfer
from params import SEND_MODE, BUFFER_SIZE

vid = cv2.VideoCapture(0)

vid.set(cv2.CAP_PROP_BUFFERSIZE, BUFFER_SIZE)

if SEND_MODE == 'usb':
    transferObj = Transfer()
    print(transferObj.get_dev())

if __name__ == '__main__':
    while True:

        ret, frame = vid.read()

        if not ret:
            continue

        scale_percent = 50

        width = int(frame.shape[1] * scale_percent / 100)
        height = int(frame.shape[0] * scale_percent / 100)
        dim = (width, height)
        frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)

        formattedFrame, data, coords, output, centers = get_colored_objects(
            frame, 
            color='blue',
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

        del frame

    cv2.destroyAllWindows()
