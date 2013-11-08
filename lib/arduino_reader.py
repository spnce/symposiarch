from decimal import Decimal
import random
import time
import datetime
from pandas import Series
import serial


class ArduinoReader:

    def __init__(self, dev_path, port=9600):
        """
        Input:
        - dev_path: Path to the Arduino device.
        - port: Port to listen on.
        """
        self.dev_path = dev_path
        self.port = port
        try:
            self.device = serial.Serial(dev_path, port)
            self.ready = True
        except:
            self.ready = False


    def read(self, secs):
        """
        Read from the serial connection for a specified number of seconds and 
        return a Pandas Series with a time stamp index.

        Input:
        - secs: Number of seconds to record

        Output:
        a Pandas Series of the recorded lines, along with a time stamp index
        """
        lines, ts = [], []
        start = time.time()
        stop = start + secs
        while time.time() < stop:
            lines.append(self.device.readline().strip())
            ts.append(datetime.datetime.fromtimestamp(time.time()))

        return Series(lines, index=ts)
