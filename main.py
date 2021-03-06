from src.common.log import *
from src.processing.server import Server
import src.hardware.camera as camera
from src.hardware.audio import Audio
import time, subprocess, signal
import sys
import atexit
import src.hardware.battery as bat


def main():
    cores = subprocess.check_output("nproc", shell=True)
    mem = subprocess.check_output("cat /proc/meminfo | grep MemTotal", shell=True)
    log.info("==========")
    # TODO cores en ram worden niet zo netjes geprint.
    log.info("David de ROW-rover! Version: %s", config["General"]["version"])
    log.info("Container running on %s cores and %s", cores, mem)
    signal.signal(signal.SIGINT, close)
    signal.signal(signal.SIGTERM, close)
    speak = Audio()
    speak.play("/app/jams/Startup.mp3", 0)
    server = Server()
    server.start()
    bat.start()
    log.debug(bat.get_batteryStatus())
    while True:
        loop()


def loop():
    time.sleep(1000)


def close(signum=0, frame=0):
    # TODO misschien iets met signum en frame doen.
    log.info("Closing down...")
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
       close()
else:
    log.crit("must be run as main, exiting")
    sys.exit(1)