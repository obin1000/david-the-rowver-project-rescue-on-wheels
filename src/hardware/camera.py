import time
import io
import threading
from src.common.log import *
import atexit

import cv2

if config["Camera"].getboolean("simulate_camera") is False:
    import picamera
    from picamera.array import PiRGBArray

"""
Declares variables to be used later on.
"""
thread = None  # background thread that reads frames from camera
frame = None  # current frame is stored here by background thread


def start():
    """
    Checks if there is a thread, if not creates and starts one.
    """
    global thread, frame
    if thread is None and config["Camera"].getboolean("simulate_camera") is False:
        # start background frame thread
        thread = thready_boy()
        time.sleep(0.5)
        thread.start()

        # wait until frames start to be available
        while frame is None:
            time.sleep(0)


def get_frame():
    """
    Is called to get frames
    @return frame as jpeg
    """
    global frame
    if config["Camera"].getboolean("simulate_camera"):
        # TODO webcam in simulatie.
        return cv2.imread("cam_emulate.jpg")
    return frame


# @atexit.register
def close():
    # TODO
    # thread.close()
    pass


# TODO deze naam zuigt, moet naar iets logicher veranderd worden.
class thready_boy(threading.Thread):
    """
    Thread to push camera to frame.
    """
    def __init__(self):
        """
        Initialise camera object.
        """
        threading.Thread.__init__(self)
        self.daemon = True
        self.camera = picamera.PiCamera()
        self.camera.resolution = (config["Camera"].getint("CAMERA_RESOLUTION_H"), config["Camera"].getint("CAMERA_RESOLUTION_V"))
        self.camera.framerate = config["Camera"].getint("framerate")
        self.rawCapture = PiRGBArray(self.camera, size=self.camera.resolution)
        self.camera.hflip = False
        self.camera.vflip = False

    def run(self):
        """
        continuous capture the camera.
        """
        global frame
        for current in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):
            frame = current.array
            self.rawCapture.truncate(0)
