from src.common.log import *
import atexit


class espeak:
    def synth(self, text="No text given"):
        log.debug("Saying: " + str(text))


class mixer:
    volume = 50

    def __init__(self, control='Master', id=0, cardindex=-1, device='default'):
        log.debug("Mixer init")

    @staticmethod
    def init():
        log.debug("Mixer init")

    def setvolume(self, volume):
        self.volume = volume
        log.debug("Volume set to " + str(volume))

    def getvolume(self):
        return self.volume

    class music:
        global vol
        global song

        @staticmethod
        def set_volume(volume):
            log.debug("Volume set to " + str(volume))
            global vol
            vol = volume

        @staticmethod
        def get_volume():
            return vol

        @staticmethod
        def load(path):
            global song
            song = path
            log.debug("Loaded audio, path: "+str(path))

        @staticmethod
        def play(loops=0):
            global song
            log.debug("Playing audio, song: "+str(song)+" loops: "+str(loops))



class PCM:
    def __init__(self, type="PCM_PLAYBACK", mode="PCM_NORMAL", device='default', cardindex=-1):
        log.debug("pcms init")