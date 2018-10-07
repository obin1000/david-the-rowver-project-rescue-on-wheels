import configparser
import time
import cv2
import numpy as np
import pickle

from src.common.log import log
# TODO camera of camera_pi verwijderen.
try:
    from picamera import PiCamera
except ImportError as error:
    log.error("ImportError: %s, normal if in fake environment", error)


class Camera:
    def get_frame(self):
        """
        Krijg de current frame van de camera.

        Returns:
           Een plaatje van de camera.
        """


        # with open('test-input-photo.pkl', 'rb') as input:
        #     photo = pickle.load(input)
        #     return photo

        # TODO config moet hij vanaf log lezen. Dit is langzaam
        config = configparser.ConfigParser()
        config.read('settings.conf')

        if config["Camera"].getboolean("simulate_camera"):
            return cv2.imread("cam_emulate.jpg", 0)


        width = config['Camera'].getint('CAMERA_RESOLUTION_H')
        height = config['Camera'].getint('CAMERA_RESOLUTION_V')

        # The horizontal resolution is rounded up to the nearest multiple of 32 pixels.
        buffer_width = int(np.math.ceil(width / 32) * 32)
        # The vertical resolution is rounded up to the nearest multiple of 16 pixels.
        buffer_height = int(np.math.ceil(height / 16) * 16)

        # create an empty buffer, with accommodation for image resolution rounding
        buffer = np.empty((buffer_height * buffer_width * 3,), dtype=np.uint8)

        self.camera.capture(buffer, 'bgr')

        # reshape buffer to image dimensions
        image = buffer.reshape((buffer_height, buffer_width, 3))

        if image is None:
            log.error("Failed to get feed from camera!")

        # reshape buffer to requested resolution
        image = image[:height, :width, :]

        # om debug info te maken
        # with open('test-input-photo.pkl', 'wb') as output:
        #     pickle.dump(image, output, pickle.HIGHEST_PROTOCOL)

        return image

    def __init__(self):
        """
        Start de camera
        """
        config = configparser.ConfigParser()
        config.read('settings.conf')

        if config["Camera"].getboolean("simulate_camera"):
            log.warn("simulate_camera: %s", True)
            return
        try:
            try:
                self.camera = PiCamera()

                # self.rawCapture = PiRGBArray(self.camera)  # dit is redundant volgens mij


                width = config['Camera'].getint('CAMERA_RESOLUTION_H')
                height = config['Camera'].getint('CAMERA_RESOLUTION_V')
                self.camera.resolution = [width, height]
                # allow camera to warm up
                time.sleep(2)

            except PiCameraError as err:
                log.error('Something went wrong with the camera:', err)
        except NameError as error:
            log.error("NameError: %s, normal if in fake environment", error)

    def close(self):
        """
        Destructor
        """
        self.camera.close()


if __name__ == "__main__":
    print("test camera")

    cam = Camera()
    img = cam.get_frame()
    cv2.imwrite("./out/camFrame.jpg", img)
    # cv2.imshow("photo", img)
    # cv2.waitKey()