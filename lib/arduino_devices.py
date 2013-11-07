import datetime
from pandas import DataFrame
from arduino_reader import ArduinoReader


class ArduinoDevice(object):
    '''
    A base class for representing an Arduino device. Actual devices inherit from this base class and
    need to implement the following methods:
    - parse_line: parsing a single line read from the device
    - score: score a pandas DataFrame representing the set of observations
    '''

    def __init__(self, dev_path, port=9600):
        '''
        Input:
        - dev_path: Path to the device
        - port: Port to listen on
        '''
        self.dev_path = dev_path
        self.port = port
        self.reader = ArduinoReader(dev_path, port)

    def parse_line(self, line):
        '''
        Method for parsing a single line, to be implemented by inheriting classes.

        Input:
        -line: A character string representing a line read from an Arduino device

        Output:
        A dict of the form {'variable_name1': value1, 'variable_name2: value2}.

        Throws an exception for lines that do not parse.
        '''
        pass

    def parse_lines(self, lines):
        '''
        Method for parsing a list of lines and generating a pandas DataFrame object from them.

        Lines that cannot be parsed by parse_line() are silently omitted.

        Input:
        - lines: List of lines, as generated by ArduinoReader.read()

        Output:
        A pandas dataframe with one column for each variable output by the device and the
        time stamp of each record as the index; each row represents one observation.
        '''

        values = []
        keep = []
        for line in lines:
            try:
                row = self.parse_line(line)
                values.append(row)
                keep.append(True)
            except:
                keep.append(False)

        df = DataFrame(values, index=lines.index[keep])
        return(df)

    def score(df):
        '''
        Method for scoring a dataframe of records, to be implemented by inheriting classes.

        Input:
        - df: A pandas DataFrame with one column for each output produced by the Arduino device and the time stamp of
              each record as the index; each row represents one observation.

        Output:
        A single numeric score.
        '''
        pass

    def measure(self, secs):
        '''
        Read from the device for a specified number of seconds, process the device output, and score it.

        Input:
        - secs: Number of seconds to read from the device for.

        Output:
        A dict containing two keys:
        - score: A single numeric score summarizing the output by the device.
        - data: A pandas DataFrame representing the data output by the device, with one column per variable and one
                row per observations. Time stamps of the observations form the index of the DataFrame.
        '''

        lines = self.reader.read(secs=secs)

        df = self.parse_lines(lines)
        score = self.score(df)

        return {'score': score, 'data': df}


class Accelerometer(ArduinoDevice):
    '''
    An Arduino accelerometer ADXL3xx
    '''

    def __init__(self, dev_path, port=9600, sample_freq='100l', discard_secs=2):
        '''
        Input:
        - dev_path: Path to the device
        - port: Port to listen on
        - sample_freq: Frequency to which observations should be resampled. Observations come in bursts it seems and
                       for the sake of scoring we want evenly spaced readings. The default '100l' represents 100
                       milliseconds.
        - discard_secs: The number of seconds to cut off from the beginning of the reading. The first few seconds
                        sometimes seem to contain noise.
        '''

        super(Accelerometer, self).__init__(dev_path=dev_path, port=port)

        self.sample_freq = sample_freq
        self.discard_secs = discard_secs

    def parse_line(self, line):
        '''
        Parse a single line read from the Arduino accelerometer.

        Input:
        - line: A character string.

        Output:
        A dict with keys x, y, and z for the three different axes of the accelerometer.
        '''

        value = [int(part) for part in line.split("\t")]

        # some rows have more than 3 values
        # discard these
        if len(value) != 3:
            raise Exception('Parse error')

        return {'x': value[0], 'y': value[1], 'z': value[2]}

    @staticmethod
    def percentile(x, perc):
        '''
        Compute a given percentile of a numeric list.

        Input:
        - x: A numeric list.
        - perc: A numeric in the range from 0 to 100

        Output:
        A number representing the desired percentile.
        '''
        x = sorted(x)
        idx = int(perc / 100.0 * len(x))
        return x[idx]

    @staticmethod
    def percentile_range(x, lower=10, upper=90):
        '''
        Compute the difference between the 90th percentile of values in a list x and the 10th percentile in the list.
        '''

        return Accelerometer.percentile(x, upper) - Accelerometer.percentile(x, lower)

    def score(self, df):
        '''
        Given a set of observations from an Arduino accelerometer, generate a score that reflects how much the
        device moved during the observation period. Specifically, this method finds the largest range from the
        90th percentile of coordinates on one axis to the 10th percentile, across the three axes. Observations from
        the first k seconds are discarded since they can be some sort of random noise.

        Input:
        - df: A pandas DataFrame representing the data output by the device, with one column per variable and one
              row per observations. Time stamps of the observations form the index of the DataFrame.

        Output:
        A single numeric score, equal to the maximum across all three axis of the difference between the 90th percentile
        and the 10th percentile of observations.
        '''
        df = df.resample(self.sample_freq, fill_method='pad')

        ## discard first k seconds
        min_t = min(df.index) + datetime.timedelta(0, self.discard_secs)
        df = df[df.index >= min_t]

        axis_scores = df.apply(Accelerometer.percentile_range)
        return max(axis_scores)


class Breathalizer(ArduinoDevice):
    '''
    An Arduino breathalizer
    '''

    def __init__(self, dev_path, port=9600, sample_freq='100l', discard_secs=2):
        '''
        Input:
        - dev_path: Path to the device
        - port: Port to listen on
        - sample_freq: Frequency to which observations should be resampled. Observations come in bursts it seems and
                       for the sake of scoring we want evenly spaced readings. The default '100l' represents 100
                       milliseconds.
        - discard_secs: The number of seconds to cut off from the beginning of the reading. The first few seconds
                        sometimes seem to contain noise.
        '''

        super(Breathalizer, self).__init__(dev_path=dev_path, port=port)

        self.sample_freq = sample_freq
        self.discard_secs = discard_secs

    def parse_line(self, line):
        '''
        Parse a single line read from the Arduino accelerometer.

        Input:
        - line: A character string.

        Output:
        A dict with key x for the reading.
        '''

        value = int(line.strip())

        return {'x': value}
