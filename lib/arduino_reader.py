import time
import datetime
from pandas import Series
import serial


class ArduinoReader:

    def __init__(self, dev_path, port=9600):
        self.dev_path = dev_path
        self.port = port
        self.device = serial.Serial(dev_path, port)


    def read(self, secs):
        '''
        Read from the serial connection for a specified number of seconds and 
        return a Pandas Series with a time stamp index.

        Input:
        - secs: Number of seconds to record

        Output:
        - lines: a Pandas Series of the recorded lines, along with a time stamp 
                 index
        '''

        lines, ts = [], []
        start = time.time()
        stop = start + secs
        while time.time() < stop:
            lines.append(self.device.readline().strip())
            ts.append(datetime.datetime.fromtimestamp(time.time()))  

        return Series(lines, index=ts)


