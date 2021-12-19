import cv2

from imageProcessing import get_objects
from transfer import Transfer

from params import PORT

vid = cv2.VideoCapture(0)
# transferObj = Transfer(PORT)

if __name__ == '__main__':
    while True:

        ret, frame = vid.read()

        formattedFrame, data, coords, output, centers = get_objects(
            frame, 
            color='all', 
            num_items_each=-1
        )

        # for entry in data:
        #     transferObj.send(entry)

        cv2.imshow('colorDetection', formattedFrame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    vid.release()

    cv2.destroyAllWindows()
