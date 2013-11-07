from pandas import DataFrame


class ArduinoDigester(object):

    def parse_line(self, line):
        pass

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

        df = DataFrame(values, index=lines.index[keep])
        return(df)


class AccelerometerDigester(ArduinoDigester):

    def parse_line(self, line):

        value = [int(part) for part in line.split("\t")]

        # some rows have more than 3 values
        # discard these
        if len(value) != 3:
            raise Exception('Parse error')

        return {'x': value[0], 'y': value[1], 'z': value[2]}
