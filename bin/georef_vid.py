'''
Georeference video screenshots for DENR project
'''

import argparse
import csv
import time
from datetime import datetime
import os
import warnings
from dateutil import parser as date_parser, tz
import bisect

# Third-party libraries
import gpxpy
from gistools.algorithm import match

CSV_TIME_FORMAT = '%M:%S'
START_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

def parse_gpx(filename):
    '''Parse a GPX file.'''

    gpx = gpxpy.parse(open(filename, 'r'))

    gpx_data = []
    for track in gpx.tracks:
        for segment in track.segments:
            #print segment.points[0].time
            for point in segment.points:
                try:
                    t = int(point.time.strftime('%s'))
                except AttributeError, e:
                    msg = 'Could not parse %s, skipping.' % str(point)
                    warnings.warn(msg)
                    continue
                gpx_data.append([t, point.latitude, point.longitude])

    return gpx_data

def parse_csv(filename, start_time, offset=0):
    '''Parse screenshot CSV file.'''

    csv_data = []
    #print start_time
    ts = int(start_time.strftime('%s'))
    with open(filename, 'rb') as fpr:
        reader = csv.reader(fpr, delimiter=',')
        for row in reader:
            tmp = time.strptime(row[0], CSV_TIME_FORMAT)
            t = int(ts + offset + tmp.tm_min * 60 + tmp.tm_sec)
            csv_data.append([t] + row[1:])

    return csv_data

def parse_start_time(time_str):
    dt = date_parser.parse(time_str).replace(tzinfo=tz.tzlocal())
    dt = dt.astimezone(tz.tzutc())
    return dt.replace(tzinfo=tz.tzlocal())
    #return dt

def georeference(csv_data, gpx_data):
    '''Georeference the CSV data using the GPX data.'''

    georef_csv_data = []
    t_gpx_seq = [row[0] for row in gpx_data]
    for row in sorted(csv_data):
        t_csv = row[0]
        (t_gpx, t_gpx_idx) = match(t_csv, t_gpx_seq)
        row = row[1:] + gpx_data[t_gpx_idx]
        georef_csv_data.append(row)

    return georef_csv_data

def dump_data(data, filename):

    with open(filename, 'wb') as fpw:
        writer = csv.writer(fpw, delimiter=',')
        for d in data:
            writer.writerow(d)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('csvfile', help='CSV file containing screenshot name and video time')
    parser.add_argument('gpxfile', help='GPX file associated with the video')
    parser.add_argument('start_time', help='Start date/time of video (yyyy-mm-dd hh:mm:ss)')
    parser.add_argument('--offset', type=float, default=0.0, 
            help='Offset from start of video (seconds)')

    args = parser.parse_args()

    # Parse 'start' argument
    start_time = parse_start_time(args.start_time)

    # Parse GPX file
    gpx_data = parse_gpx(args.gpxfile)
    dump_data(gpx_data, 'gpx.dump')

    # Parse CSV file
    csv_data = parse_csv(args.csvfile, start_time, args.offset)
    dump_data(csv_data, 'csv.dump')

    # Georeference the screenshots using the GPX file 
    georef_csv_data = georeference(csv_data, gpx_data)

    # Write to output CSV file 
    outfn = '_georef'.join(os.path.splitext(args.csvfile))
    writer = csv.writer(open(outfn, 'wb'), delimiter=',')
    for row in georef_csv_data:
        writer.writerow(row)


