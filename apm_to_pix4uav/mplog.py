#! /usr/bin/python

import sys
import csv

header_str = [
                'Current Pitch',
                'Current Roll',
                'Desired Altitude',
                'Y Acceleration',
                'Desired Roll',
                'GPS Heading',
                'Location East',
                'Location North',
                'Desired Pitch',
                'GPS Speed'
             ]


class MPLog:

    def __init__(self, logfile=None):
        if logfile:
            fp = open(logfile, 'rb')
            reader = csv.reader(fp, delimiter=' ')
            self.data = []
            for row in reader:
                self.data.append(row)
            fp.close()
            self.filename = logfile

    def clear_for_pix4uav(self):
        '''All fields not used by Pix4UAV are set to zero.'''

        for row in self.data:
            for i in range(len(row)):
                if i != 32 and i != 24 and i != 25 and i != 50 and i != 19:
                    row[i] = 0

    def write(self, filename=None):
        if not filename:
            filename = self.filename

        fp = open(filename, 'wb')
        writer = csv.writer(fp, delimiter=' ')
        for row in self.data:
            writer.writerow(row)


if __name__ == '__main__':
    infile = sys.argv[1]
    outfile = sys.argv[2]

    log = MPLog(infile)
    log.clear_for_pix4uav()
    log.write(outfile)

