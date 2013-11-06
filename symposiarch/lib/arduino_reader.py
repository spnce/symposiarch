import random
import time
import serial


class ArduinoReader:

    def __init__(self):
        pass

    def estimate_blood_alcohol_concentration(self, seconds):
        # read data from the arduino alcohol sensor for a number of seconds
        time.sleep(seconds)
        # process the data into a blood alcohol concentration estimate
        bac = random.randint(0, 1000) / 1000
        # return the BAC estimate
        return bac