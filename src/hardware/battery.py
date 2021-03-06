from src.common.log import *

if config["Battery"].getboolean("simulate_battery") is False:
    import smbus2 as smbus
else:
    import src.dummy.smbus2dummy as smbus

battery_value = 0
def start():
    """
    Join the I²C bus as master
    """
    global bus
    bus = smbus.SMBus(1)


def get_batteryStatus():
    """
    get the battery percentage.
    @return: int 0-100
    """
    global bus, battery_value
    try:
        battery_value = bus.read_byte_data(int(config["Battery"]["I2C_slave_address"], 16), 0)
    except IOError as err:
        log.error("IOError while reading battery status: %s", str(err))
    return battery_value