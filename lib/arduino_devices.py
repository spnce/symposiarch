import datetime
import math
from pandas import DataFrame
from arduino_reader import ArduinoReader


class ArduinoDevice(object):
    '''
    A base class for representing an Arduino device. Actual devices inherit from this base class and
    need to implement the following methods:
    - parse_line: parsing a single line read from the device
    - score: score a pandas DataFrame representing the set of observations
    '''

    def __init__(self, dev_path, port=9600, range_low=0, range_high=1):
        '''
        Input:
        - dev_path: Path to the device
        - port: Port to listen on
        - range_low: The minimum value expected from the measure() method
        - range_high: The maximum value expected from the measure() method

        The parameters range_low and range_high are used for faking data if the device connection fails.
        '''
        self.dev_path = dev_path
        self.port = port
        self.reader = ArduinoReader(dev_path, port)
        self.range_low = range_low
        self.range_high = range_high

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

    def score(self, df):
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
        A numeric scalar
        '''

        if self.reader.ready:
            lines = self.reader.read(secs=secs)

            df = self.parse_lines(lines)
            score = self.score(df)
        else:
            score = self.random_score()

        return score

    def random_score(self):
        low = int(self.range_low * 1000)
        high = int(self.range_high * 1000)
        score = Decimal(random.randint(low, high) / 1000)

        score = Decimal(0.999)
        return score

    def test(self, secs):
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

        if self.reader.ready:
            lines = self.reader.read(secs=secs)

            df = self.parse_lines(lines)
            score = self.score(df)
        else:
            score = self.random_score()

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

    def __init__(self, dev_path, port=9600, sample_freq='100l', discard_secs=0.5):
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

    def score(self, df):
        '''
        Given a set of observations from an Arduino breathalizer, generate a score that reflects how much the
        values recorded during the observation period changed.

        Input:
        - df: A pandas DataFrame representing the data output by the device, with one column per variable and one
              row per observations. Time stamps of the observations form the index of the DataFrame.

        Output:
        A single numeric score, equal to the difference between the minimum value and the maximum value.
        '''

        df = df.resample(self.sample_freq, fill_method='pad')

        ## discard first k seconds
        min_t = min(df.index) + datetime.timedelta(0, self.discard_secs)
        df = df[df.index >= min_t]

        range = df.x.max() - df.x.min()

        return range

class Acceleralizer(ArduinoDevice):
    '''
    An Arduino accelerometer and breathalizer
    '''

    def __init__(self, dev_path, port=9600, sample_freq='100l', discard_secs=0.5):
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

        super(Acceleralizer, self).__init__(dev_path=dev_path, port=port)

        self.sample_freq = sample_freq
        self.discard_secs = discard_secs

    def parse_line(self, line):
        '''
        Parse a single line read from the Arduino accelerometer.

        Input:
        - line: A character string.

        Output:
        A dict with keys x, y, and z for the three different axes of the accelerometer, as well as a key 'bac' for
        the breathalizer reading.
        '''

        value = [int(part) for part in line.split("\t")]

        # some rows have more than 4 values
        # discard these
        if len(value) != 4:
            raise Exception('Parse error')

        return {'x': value[0], 'y': value[1], 'z': value[2], 'bac': value[3]}

    def score(self, df):
        '''
        Given a set of observations from an Arduino accelerometer and a breathalizer, generate a score that reflects
        how much the values recorded during the observation period changed.

        Input:
        - df: A pandas DataFrame representing the data output by the device, with one column per variable and one
              row per observations. Time stamps of the observations form the index of the DataFrame.

        Output:
        A single numeric score,[[

        '''

        df = df.resample(self.sample_freq, fill_method='pad')

        ## discard first k seconds
        min_t = min(df.index) + datetime.timedelta(0, self.discard_secs)
        df = df[df.index >= min_t]

        baseline_end = min(df.index) + datetime.timedelta(0, 0.5)
        base_df = df[df.index <= baseline_end]
        base_avg = base_df.bac.mean()
        base_sd = math.sqrt(base_df.bac.var())

        df['bac_z'] = (df.bac - base_avg) / base_sd

        min_z = 0.5 * df.bac_z.max()
        breath_start = min(df[df.bac_z >= min_z].index)
        test_start = breath_start + datetime.timedelta(0, 1)
        test_end = breath_start + datetime.timedelta(0, 2)

        accel_ranges = df[(df.index >= test_start) & (df.index <= test_end)].apply(Accelerometer.percentile_range)
        accel_range = max(accel_ranges)

        bac_range = df.bac.max() - df.bac.min()
        if bac_range < 50:
            bac_range = 0
        bac = self.scale_bac(bac_range, raw_min=df.bac.min(), raw_max=1023, scaled_min=0.0, scaled_max=0.2)

        return bac

    def scale_bac(self, raw_value, raw_min, raw_max, scaled_min, scaled_max):

        return raw_value / (raw_max - raw_min) * (scaled_max - scaled_min)