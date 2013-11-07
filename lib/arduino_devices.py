from scipy import stats
import datetime
from arduino_reader import ArduinoReader
from signal_digesters import AccelerometerDigester


class ArduinoDevice(object):

    def __init__(self, dev_path, digester):

        self.dev_path = dev_path
        self.reader = ArduinoReader(dev_path=dev_path)
        self.digester = digester

    def score(df):
        pass

    def measure(self, secs):
        lines = self.reader.read(secs=secs)

        df = self.digester.parse_lines(lines)
        score = self.score(df)

        return {'score': score, 'data': df}


class Accelerometer(ArduinoDevice):


    def __init__(self, dev_path, sample_freq='100l', discard_secs=2):

        super(Accelerometer, self).__init__(dev_path=dev_path, digester=AccelerometerDigester())

        self.sample_freq = sample_freq
        self.discard_secs = discard_secs


    @staticmethod
    def percentile_range(x, lower = 10, upper = 90):
        low = stats.scoreatpercentile(x, lower)
        high = stats.scoreatpercentile(x, upper)
        return (high - low)

    def score(self, df):
        df = df.resample(self.sample_freq, fill_method='pad')

        ## discard first k seconds
        min_t = min(df.index) + datetime.timedelta(0, self.discard_secs)
        df = df[df.index >= min_t]

        axis_scores = df.apply(Accelerometer.percentile_range)
        return max(axis_scores)


