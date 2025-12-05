# camera.py

import cv2
from config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT

class Camera:
    def __init__(self):
        self.cap = None

    def open(self):
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

        if not self.cap.isOpened():
            raise RuntimeError("Failed to open camera.")

    def read(self):
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Failed to read frame from camera.")
        return frame

    def release(self):
        if self.cap:
            self.cap.release()
