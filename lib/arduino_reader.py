from decimal import Decimal
import random
import time
import datetime
import numpy as np
import pandas as pd
import serial
from scipy import stats


class ArduinoReader:

    def __init__(self, accel_device):
        self.accel_device = accel_device
        self.accel_serial = serial.Serial(self.accel_device, 9600)


    def estimate_blood_alcohol_concentration(self, seconds):
        # read data from the arduino alcohol sensor for a number of seconds
        time.sleep(seconds)
        # process the data into a blood alcohol concentration estimate
        bac = Decimal(random.randint(0, 1000)) / 1000
        # return the BAC estimate
        return bac


    def arduino_read(self, secs):
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
            lines.append(self.accel_serial.readline().strip())
            ts.append(datetime.datetime.fromtimestamp(time.time()))  

        return(pd.Series(lines, index = ts))

    @staticmethod
    def parse_line_accel(line):

        val  = [int(part) for part in line.split("\t")]

        # some rows have more than 3 values
        # discard these
        if len(val) != 3:
            raise Exception('Parse error')

        return {'x': val[0], 'y': val[1], 'z': val[2]}


    @staticmethod
    def parse_lines(lines, parse_func):

        vals = []
        keep = []
        for line in lines:
            try:
                row = parse_func(line)
                vals.append(row)
                keep.append(True)
            except:
                keep.append(False)

        df = pd.DataFrame(vals, index = lines.index[keep])    
        return(df)

    @staticmethod
    def percentile_range(x, lower = 10, upper = 90):
        low = stats.scoreatpercentile(x, lower)
        high = stats.scoreatpercentile(x, upper)
        return (high - low)

    @staticmethod
    def score_accel(df):
        df = df.resample('100l', fill_method = 'pad')

        ## discard first 2 seconds
        min_t = min(df.index) + datetime.timedelta(0, 2)
        df = df[df.index >= min_t]

        axis_scores = df.apply(ArduinoReader.percentile_range)
        return(max(axis_scores))


    def measure_accel(self, secs):

        lines = self.arduino_read(secs = secs)

        df = ArduinoReader.parse_lines(lines, ArduinoReader.parse_line_accel)
        score = ArduinoReader.score_accel(df)

        return({'score': score, 'data': df})
