from src.common.log import *
import time
if config["Motor"].getboolean("simulate_motor") is False:
    import smbus2 as smbus
else:
    import src.dummy.smbus2dummy as smbus


class motor:
    __Instance = None
    OFFSET = 0  # offset in the array
    ADDRESS = 0x32  # I2c address of the motorcontroller
    # speed from 4 to 250
    speedl = 0
    speedr = 0
    # 0 = stilstaan 2 = vooruit 1 = achteruit
    richtingl = 0
    richtingr = 0

    stop = [7, 3, 0, 0, 3, 0, 0]
    lastSendData = [7, 0, 0, 0, 0, 0, 0]
    lastSendTime = 0

    history = []

    def __init__(self):
        """
        Initilizes a motor object, but only one. To use this class, use getInstance instead.
        @raises: exception when a instance of this class already exists
        """
        if motor.__Instance is not None:
            raise Exception("Instance already exists")
        else:
            motor.__Instance = self
            self.bus = smbus.SMBus(1)  # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
            self.leftright(0, 0)
            self.lastSendTime = time.time()

    @staticmethod
    def getInstance():
        """
        Initializes a motor object, but only one
        @return: The single only instance of this class
        """
        if motor.__Instance is None:
            motor()
        return motor.__Instance

    def __del__(self):
        """
        Closes the i2c bus.
        """
        self.leftright(0, 0)
        self.bus.close()

    def leftright(self, speedl: int, speedr: int) -> bool:
        """
        Combines the functionalities of left and right
        @return: returns a bool based on success
        @param speedl: Speed wheels left range from -255 to 255
        @param speedr: Speed wheels right range from -255 to 255
        """
        if speedl > -256 and speedl < 256:
            if speedl == 0:
                self.speedl = 0
                self.richtingl = 0
            if speedl > 0:
                self.speedl = speedl
                self.richtingl = 2
            if speedl < 0:
                self.speedl = -speedl
                self.richtingl = 1
        else:
            raise ValueError("{0} is not in the range of -255 to 255".format(speedl))

        if speedr > -256 and speedr < 256:
            if speedr == 0:
                self.speedr = 0
                self.richtingr = 0
            if speedr > 0:
                self.speedr = speedr
                self.richtingr = 2
            if speedr < 0:
                self.speedr = -speedr
                self.richtingr = 1
        else:
            raise ValueError("{0} is not in the range of -255 to 255".format(speedr))

        if self._send_data():
            return True
        else:
            return False

    def left(self, speed: int) -> bool:
        """
        Speed and direction of the left wheels
        @param speed: Range from -255 to 255
        @return: returns a bool based on success
        @raises: Value error when speed is out of the range
        """
        if speed > -256 and speed < 256:
            if speed == 0:
                self.speedl = 0
                self.richtingl = 0
            if speed > 0:
                self.speedl = speed
                self.richtingl = 2
            if speed < 0:
                self.speedl = -speed
                self.richtingl = 1
        else:
            raise ValueError("{0} is not in the range of -255 to 255".format(speed))
        if self._send_data():
            return True
        else:
            return False

    def right(self, speed: int) -> bool:
        """
        Speed and direction of the right wheels
        @param speed: Range from -255 to 255
        @return: returns a bool based on success
        @raises: Value error when speed is out of the range
        """
        if speed > -256 and speed < 256:
            if speed == 0:
                self.speedr = 0
                self.richtingr = 0
            if speed > 0:
                self.speedr = speed
                self.richtingr = 2
            if speed < 0:
                self.speedr = -speed
                self.richtingr = 1
        else:
            raise ValueError("{0} is not in the range of -255 to 255".format(speed))
        if self._send_data():
            return True
        else:
            return False

    def status(self) -> dict:
        """
        Generates the current state of the motor
        @return: returns a dictionary with the status
        """
        return {
            "speedl": self.speedl,
            "richtingl": self.richtingl,
            "speedr": self.speedr,
            "richtingr": self.richtingr
        }

    def get_value_left(self) -> int:
        """
        Get left speed value
        @return (int): value
        """
        return self.speedl

    def get_value_right(self) -> int:
        """
        Get right speed value
        @return (int): value
        """
        return self.speedr

    def get_richting_left(self) -> int:
        """
        Get left direction value
        @return (int): value
        """
        return self.richtingl

    def get_richting_right(self) -> int:
        """
        Get right direction value
        @return (int): value
        """
        return self.richtingr

    def _send_data(self) -> bool:
        """
        generate an array of data for the motorcontroller and sends it over the I2C bus
        @return: returns a bool based on success
        """
        try:
            motor_data = [7, 3, self.speedl, self.richtingl, 3, self.speedr, self.richtingr]
            if motor_data is not self.lastSendData:
                self.bus.write_i2c_block_data(self.ADDRESS, self.OFFSET, motor_data)
                self.saveLocation(self.lastSendData)
                self.lastSendData = motor_data
        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
            return False
        else:
            return True

    def saveLocation(self, motor_data):
        """
        Save a combiantion of motordata and time it lasted in the history
        @param motor_data: The command that was executed since the last save
        """
        now = time.time()
        timedifference = now - self.lastSendTime
        self.lastSendTime = now
        data = {
            "motor": motor_data,
            "time": timedifference
        }
        self.history.append(data)

    def moveBack(self):
        """
        Move the rover back to its starting position
        """
        log.debug("Starting drive back")
        while True:
            if len(self.history) > 1:
                instruction = self.history.pop()
                log.debug(instruction)
            else:
                log.debug("Returned to start")
                self.leftright(0, 0)
                self.history = []
                break

            data = instruction.get("motor")
            if data[3] is 2:
                data[3] = 1
            elif data[3] is 1:
                data[3] = 2

            if data[6] is 2:
                data[6] = 1
            elif data[6] is 1:
                data[6] = 2

            self.bus.write_i2c_block_data(self.ADDRESS, self.OFFSET, data)
            if data is self.stop:
                time.sleep(0.5)
            else:
                time.sleep(instruction.get("time"))
