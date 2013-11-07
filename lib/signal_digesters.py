import pandas as pd


class ArduinoDigester(object):

    def parse_line(self, line):        
        raise Exception('Not implemented')


    def parse_lines(self, lines):

        values = []
        keep = []
        for line in lines:
            try:
                row = self.parse_line(line)
                values.append(row)
                keep.append(True)
            except:
                keep.append(False)

        df = pd.DataFrame(values, index=lines.index[keep])
        return(df)


class AccelerometerDigester(ArduinoDigester):


    def parse_line(self, line):

        val  = [int(part) for part in line.split("\t")]

        # some rows have more than 3 values
        # discard these
        if len(val) != 3:
            raise Exception('Parse error')

        return {'x': val[0], 'y': val[1], 'z': val[2]}

