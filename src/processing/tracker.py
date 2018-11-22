from src.common.log import *
import threading
import math
import time
from src.hardware.motor import motor
from src.hardware.compas import Compas
if config["Tracker"].getboolean("simulate_tracker") is False:
    import RPi.GPIO as GPIO
else:
    import src.dummy.GPIOdummy as GPIO


class Tracker(threading.Thread):
    __Instance = None
    history = []
    # variables for the Wheelencoders
    INTERVALSPEED = 0.5  # seconds
    ENCODERPINL = 12
    ENCODERPINR = 11
    ENCODERHOLES = 20
    ENCODERDIAMETER = 20.0  # mm full wheel is 24.0
    ENCODERCIRCUMFERENCE = (math.pi*ENCODERDIAMETER)/1000.0  # meters
    ENCODERHOLEDISTANCE = ENCODERCIRCUMFERENCE/ENCODERHOLES  # meters
    encoderPulsesL = 0
    encoderSpeedL = 0  # meters/second
    encoderPulsesR = 0
    encoderSpeedR = 0  # meters/second
    lastCapture = 0

    def interruptPulseL(self, channel):
        """
        Called by the wheel encoder when it creates a pulse, count the number of pulses
        @param channel: The pin of the interrupt
        """
        self.encoderPulsesL += 1

    def interruptPulseR(self, channel):
        """
        Called by the wheel encoder when it creates a pulse, count the number of pulses
        @param channel: The pin of the interrupt
        """
        self.encoderPulsesR += 1

    def __init__(self):
        """
        Initilizes a tracker object, but only one. To use this class, use getInstance instead.
        @raises: exception when a instance of this class already exists
        """
        if Tracker.__Instance is not None:
            raise Exception("Instance already exists")
        else:
            threading.Thread.__init__(self)
            Tracker.__Instance = self
            GPIO.setmode(GPIO.BOARD)
            # Wheelencoder Left
            GPIO.setup(self.ENCODERPINL, GPIO.IN)
            GPIO.add_event_detect(self.ENCODERPINL, GPIO.RISING, callback=self.interruptPulseL)
            # Wheelencoder right
            GPIO.setup(self.ENCODERPINR, GPIO.IN)
            GPIO.add_event_detect(self.ENCODERPINR, GPIO.RISING, callback=self.interruptPulseR)
            self.start()

    def __del__(self):
        """
        Closes the i2c bus.
        """
        GPIO.cleanup()

    @staticmethod
    def getInstance():
        """
        Initializes a tracker object, but only one
        @return: The single only instance of this class
        """
        if Tracker.__Instance is None:
            Tracker()
        return Tracker.__Instance

    def run(self):
        self.lastCapture = time.time()
        while True:
            # log.debug(str(self.encoderPulsesL)+" "+str(self.encoderPulsesR)+" "+str(Compas.getInstance().getDegree()))
            now = time.time()
            timedifference = now-self.lastCapture
            self.encoderSpeedL = (self.encoderPulsesL*self.ENCODERHOLEDISTANCE)/timedifference
            self.encoderSpeedR = (self.encoderPulsesR*self.ENCODERHOLEDISTANCE)/timedifference
            self.encoderPulsesL = 1
            self.encoderPulsesR = 1
            self.lastCapture = now
            self.saveLocation()
            time.sleep(self.INTERVALSPEED)

    def saveLocation(self):
        data = {
            "speed": self.getSpeed(),
            "curve": self.getCurve(),
            "direction": Compas.getInstance().getDegree()
        }
        self.history.append(data)

    def getSpeed(self):
        return (self.encoderSpeedR+self.encoderPulsesL)-self.getCurve()

    def getCurve(self):
        """
        Calculates if the rover is making a turn at the moment
        @return: float value of how much the rover is turning and to which direction range:
        """
        if motor.getInstance().get_richting_right() is 1:
            speedR = -self.encoderSpeedR
        else:
            speedR = self.encoderSpeedR

        log.debug(str(motor.getInstance().get_richting_right() )+" "+str(motor.getInstance().get_richting_left() ))

        if motor.getInstance().get_richting_left() is 1:
            speedL = -self.encoderSpeedL
        else:
            speedL = self.encoderSpeedL

        log.debug(str(speedL)+" "+str(speedR))

        return speedR - speedL

    def moveBack(self):
        while True:
            instruction = self.history.pop()
            # TODO get to the choppah

    def locationToMove(self, location):
        pass


