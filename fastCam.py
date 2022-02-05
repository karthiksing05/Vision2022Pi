import cv2
import threading
from threading import Lock

class Camera(object):

    last_frame = None
    last_ready = None
    lock = Lock()
    capture = None

    def __init__(self, rtsp_link):
        self.capture = cv2.VideoCapture(rtsp_link)
        thread = threading.Thread(target=self.rtsp_cam_buffer, args=(), name="rtsp_read_thread")
        thread.daemon = True
        thread.start()

    def rtsp_cam_buffer(self):
        while True:
            with self.lock:
                self.last_ready = self.capture.grab()

    def getFrame(self):
        if (self.last_ready is not None):
            self.last_ready,self.last_frame=self.capture.retrieve()
            return True, self.last_frame.copy()
        else:
            return False, -1
