# camera.py
import cv2
import numpy as np

class Camera:
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        
        self.cap = cv2.VideoCapture("/dev/video2") # change to 0, 1, 2, etc for other cams
        
        if not self.cap.isOpened():
            raise RuntimeError("cant open cam")
        
        # set res
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def get_frame(self):

        ret, frame = self.cap.read()
        if not ret:
            # if fail, show black frame
            return np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # bgr -> rgb
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def release(self):
        self.cap.release()

