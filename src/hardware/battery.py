from src.common.log import *

if config["Battery"].getboolean("simulate_Battery") is False:
    import smbus2 as smbus
else:
    import src.dummy.smbus2dummy as smbus


def start():
    global bus
    bus = smbus.SMBus(1)


def get_batteryStatus():
    global bus
    return bus.read_byte_data(int(config["Battery"]["I2C_slave_address"], 16), 0)
