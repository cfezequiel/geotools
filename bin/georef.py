#! /usr/bin/python

'''
Georeferences a set of images with GPS/IMU information.

Currently supports APM log files only.

author: Carlos F. Ezequiel
version: 2.5
'''

import logging 
import re
import argparse
import csv
from os import listdir, path, walk
import imghdr
from math import sqrt
import time
from fnmatch import fnmatch
import warnings

# From package
from gistools import timeutil
from gistools.algorithm import match

#======================== SETTINGS =========================
# Reporting
report_filename = 'report_georef_%s.txt' % time.strftime('%Y_%m_%d_%H_%M_%S')
logging.basicConfig(
        filename=report_filename, 
        level=logging.INFO,
        format='%(levelname)s:%(message)s'
        )

# Acceptable images
image_ext = ['tiff', 'jpg', 'jpeg']

# Leap seconds between UTC and GPS times
leap_seconds = 16

# Multiplier
multiplier = {'ms': 1000, 's':1}

# Initial image vs. CAM trigger time difference threshold (ms)
image_cam_time_threshold = 60000 # 1 minute

#============================================================

class Image:
    '''Image information.'''

    def __init__(self, name, root_dir='.'):
        self.__name = name
        self.__root_dir = root_dir
        self.__time_created = self.__get_time_created(root_dir + '/' + name)

    def __get_time_created(self, fn):
        '''Get creation time in seconds after epoch time.'''

        t = timeutil.get_timestamp(fn)
        ts = timeutil.gps_seconds(t)

        # Convert to GPS milliseconds
        ts *= multiplier['ms']

        return ts

    def filename(self):
        return self.__name

    def filepath(self):
        return self.__root_dir + '/' + self.__name

    def timestamp(self):
        '''Return timestamp as GPS milliseconds since start of week.'''

        return self.__time_created

    def __repr__(self):
        return str([self.filename(), self.timestamp(), self.__root_dir])

class GPS:
    def __init__(self, lat, lon, alt=0):
        self.lat = lat
        self.lon = lon
        self.alt = alt

class IMU:
    def __init__(self, roll, pitch, yaw):
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw

class Pose:
    '''UAV pose, which includes GPS and IMU information'''

    def __init__(self, time, gps, imu=None):
        self.__time = time
        self.__gps = gps
        self.__imu = imu

    def __repr__(self):
        return str((self.__time) + self.data())

    def gps(self):
        return self.__gps

    def imu(self):
        return self.__imu

    def timestamp(self):
        return self.__time

    def data(self):
        t = (self.__gps.lat, self.__gps.lon, self.__gps.alt)
        if self.__imu:
            t += (self.__imu.roll, self.__imu.pitch, self.__imu.yaw)
        return t

def get_apm_version(logfile):
    '''Get APM version number (Vx.xx) of an APM log file.'''

    with open(logfile, 'rt') as fp:
        version = ''
        while True:
            line = fp.readline()
            if line.find('ArduPlane') >= 0:
                version_str = line.split()[1]
                # Strip version number of non-numerical/decimal characters
                non_decimal = re.compile(r'[^\d.]+')
                version = float(non_decimal.sub('', version_str))
                break
            elif line == '':
                break
        return version

def gps_to_local_time(gps_seconds, gps_week):
    '''Convert GPS time to local time_struct (see time module).'''
    pass #TODO

def isimage(filename):
    try:
        ext = imghdr.what(filename)
    except IOError:
        return False

    if ext in image_ext:
        return True

    return False

def get_images(source_dir):
    assert path.exists(source_dir)
    assert path.isdir(source_dir)
    images = []

    # Read images from source directory
    root = source_dir
    files = listdir(root)
    images = [Image(f, root) for f in files if isimage(root + '/' + f)]

    # Sort images by time
    images.sort(key=lambda image: image.timestamp())

    return images

def get_logfile(source_dir):
    assert path.exists(source_dir)
    assert path.isdir(source_dir)

    # Get the first *.log file found in source directory
    for fn in listdir(source_dir):
        if fnmatch(fn, '*.log'):
            return source_dir + '/' + fn

def get_logfile_type(logfile):
    #FIXME: for now, assume logfile is APM
    return 'APM'

def parse_apm_log_file(logfile):
    '''Read CAM entries from APM log file, which define the UAV pose at time camera was triggered.'''

    # Open log file
    fp = open(logfile, 'r')

    # Get version number
    version = get_apm_version(logfile)

    # Get CAM entries
    cam_entries = []
    for line in fp.readlines():
        if line.split(',')[0] == 'CAM':
            cam_entries.append(line)

    reader = csv.reader(cam_entries, delimiter=',')
    pose_info= []
    if version >= 2.76:
        # Add offset since GPS lat field starts at row[3]
        offset = 1 
    else:
        # GPS lat field starts at row[2]
        offset = 0
    for row in reader:
        #time = int(row[1]) / multiplier['ms']
        # Use GPS milliseconds for timestamps
        time = int(row[1])
        gps = GPS(float(row[2 + offset]), float(row[3 + offset]), float(row[4 + offset]))
        imu = IMU(float(row[5 + offset]), float(row[6 + offset]), float(row[7 + offset]))
        pose = Pose(time, gps, imu)
        pose_info.append(pose)

    # Sort
    pose_info.sort(key=lambda pi: pi.timestamp())

    return pose_info 

def parse_apm_gpx_file(gpx_file):
    '''Parse an APM GPX file for Pose information.'''

    # TODO
    pass

def unique_pairs(pairs):
    '''Make list of pairs unique (i.e. remove duplicates).'''

    seen = set()
    unique_pairs = [(x, y) for x,y in pairs if x not in seen and not seen.add(x)]

    return unique_pairs

def interpolate_nn(ts_images, ts_pose_info, analyze=False):
    '''Perform nearest-neighbor interpolation for georeferencing.'''

    image_times = sorted(ts_images.keys());
    pose_times = sorted(ts_pose_info.keys());

    pairings = []
    pose_times_idx_lo = 0
    for image_time in image_times:
        (pose_time, pose_times_idx_lo) = match(image_time, pose_times, pose_times_idx_lo)
        pairings.append((image_time, pose_time))

    # Filter out duplicates
    #FIXME: do not remove duplicates for analysis
    #image_pose_pairs = unique_pairs(pairings)
    image_pose_pairs = pairings

    # Pair image and pose_info data
    georef_images = []
    for image_time, pose_time in pairings:
        georef_images.append((ts_images[image_time], ts_pose_info[pose_time]))

    # Do some post-processing analysis
    if analyze:
        errors = []
        no_matches = 0
        duplicate_images = 0
        #pose_ts_list = [p[1] for p in image_pose_pairs]
        for pose_ts in pose_times:
            indices = [i for i, x in enumerate(image_pose_pairs) if x[1] == pose_ts]
            image_ts_list = [image_pose_pairs[i][0] for i in indices]
            if image_ts_list:
                if len(image_ts_list) > 1:
                    duplicate_images += len(image_ts_list)
                for image_ts in image_ts_list:
                    error = abs(image_ts - pose_ts)
                    errors.append(error)
                    logging.info('Pose(t=%d) <- Image(t=%d): error = %d' % (pose_ts, image_ts, error))
            else:
                no_matches += 1
                logging.info('Pose(t=%d)' % pose_ts)
        mse = (1.0/len(errors)) * sum([e**2 for e in errors])
        logging.info('Root-mean-squared-error (rmse) = %.2fms' % sqrt(mse))
        logging.info('Number of pose entries without match: %d' % no_matches)
        logging.info('Number of images with duplicate pose matchings: %d' % duplicate_images)

    return georef_images

def interpolate_linear(ts_images, ts_pose_info, analyze=False):
    '''Perform linear interpolation for georeferencing.'''

    seq_ti = sorted(ts_images.keys());
    seq_tp = sorted(ts_pose_info.keys());

    lerp = lambda x, y0, y1, tau: tau * y1 + (1 - tau) * y0

    tp_idx_lo = 0
    geo_images = []
    for ti in seq_ti:
        (tp, tp_idx_lo) = match(ti, seq_tp, y_idx_lo=tp_idx_lo, match_low_only=True)
        if tp_idx_lo >= len(seq_tp) - 1:
            #FIXME: is this valid, just copy the best match?
            geo_images.append((ts_images[ti], ts_pose_info[tp]))
        else:
            tp_idx = tp_idx_lo + 1
            x = ti 
            x0 = tp
            x1 = seq_tp[tp_idx]
            if analyze:
                logging.info("image(%d) interpolated in pose_range [%d, %d]" % (x, x0, x1))
            # Multiply by 1.0 for floating-point precision
            tau = 1.0 * (x - x0) / (x1 - x0)
            pint = []
            for y0, y1 in zip(ts_pose_info[x0].data(), ts_pose_info[x1].data()):
                y = lerp(x, y0, y1, tau)
                pint.append(y)
            if len(pint) > 3:
                pose = Pose(ti, GPS(pint[0], pint[1], pint[2]), IMU(pint[3], pint[4], pint[5]))
            else:
                pose = Pose(ti, GPS(pint[0], pint[1], pint[2]))
            geo_images.append((ts_images[ti], pose))

    return geo_images

def spread_duplicates(seq):
    '''Spread duplicate seqtamps so that they have different values.'''

    dup = dict()
    seen = set()
    for t in seq:
        if t in seen:
            if not dup.has_key(t):
                dup[t] = 1
            else:
                dup[t] += 1
        else:
            seen.add(t)
    unique = list(seen)
    new_seq = list(seq)
    for d in sorted(dup.keys()):
        n = dup[d] + 1
        i0 = seq.index(d)
        t0 = seq[i0]
        i1 = i0 + n
        if i1 >= len(seq):
            t1 = seq[-1] + 1
        else:
            t1 = seq[i1]
        delta = 1.0 * (t1 - t0) / n
        for i in range(n - 1):
            new_seq[i0 + i + 1] = seq[i0 + i + 1] + delta * (i + 1)

    return new_seq

def georeference_images(images, pose_info, offset=0, algorithm='nearest_neighbor', analyze=False,
        abs_time=False):

    # Get initial times
    if not abs_time:
        image_t0 = images[0].timestamp()
        pose_t0 = pose_info[0].timestamp()

    # Create dictionary of image and pose timestamps based on their initial times
    # respectively
    if abs_time:
        ts_images_list = [(image.timestamp() + offset, image) for image in images]
    else:
        ts_images_list = [(image.timestamp() - image_t0, image) for image in images]
    ts_i = spread_duplicates([t for t,i in ts_images_list])
    ts_images = dict([(t, ti[1]) for t,ti in zip(ts_i, ts_images_list)])
    if abs_time:
        ts_pose_info_list = [(pose.timestamp(), pose) for pose in pose_info]
    else:
        ts_pose_info_list = [(pose.timestamp() - pose_t0, pose) for pose in pose_info]
    ts_p = spread_duplicates([t for t,p in ts_pose_info_list])
    #ts_p = [t for t,p in ts_pose_info_list]
    ts_pose_info = dict([(t, tp[1]) for t,tp in zip(ts_p, ts_pose_info_list)])

    # Run interpolation algorithm
    if algorithm == 'nearest_neighbor':
        georef_images = interpolate_nn(ts_images, ts_pose_info, analyze)
    elif algorithm == 'linear':
        georef_images = interpolate_linear(ts_images, ts_pose_info, analyze)

    return georef_images

def gen_pix4uav_file(geo_images, output_file, exclude_imu=False, header=False, ext=None):

    with open(output_file, 'wb') as outfp:
        writer = csv.writer(outfp, delimiter=',')
        fmt6 = '{:.6f}'
        fmt2 = '{:.2f}'
        if header:
            writer.writerow(['Filename', 'GPSlat', 'GPSlon', 'GPSalt', 'Yaw', 'Pitch', 'Roll'])
        for image, pose in geo_images:
            gps = pose.gps()
            if ext:
                (b, e) = path.splitext(image.filename())
                filename = b + '.' + ext
            else:
                filename = image.filename()
            entry = [filename, fmt6.format(gps.lat), fmt6.format(gps.lon), fmt2.format(gps.alt)]
            imu = pose.imu()
            if not exclude_imu and imu:
                entry += [fmt2.format(imu.yaw), fmt2.format(imu.pitch), fmt2.format(imu.roll)]
            writer.writerow(entry)
            
if __name__ == '__main__':

    # Parse arguments
    parser = argparse.ArgumentParser(
            description=
            '''
            Create georeferencing CSV file from images and GPS logs. 
            Performs nearest-neighbor interpolation by default.
            Generates a report after completion.
            '''
            , epilog=
            '''
            Note: In order to produce good georeferencing of images, make sure that the first image 
            and the first Pose entry of the APM log have near-matching timestamps (error at most 2s).
            '''
            )
    parser.add_argument('source', type=str, 
            help='Source directory for images and the APM log file (*.log)')
    parser.add_argument('--logfile', type=str, default=None,
            help='APM log file (*.log)')
    parser.add_argument('-o', '--output', default='georef.csv', 
            help='Output Pix4UAV file [default: georef.csv]')
    parser.add_argument('-d', '--output_dir', 
            help='Set the output directory for the pix4UAV file [default: source directory]')
    parser.add_argument('--exclude_imu', action='store_true', 
            help='Exclude IMU info (yaw, pitch, roll) from output file')
    parser.add_argument('--analyze', action='store_true', default=False,
            help='Output image-pose matching information')
    parser.add_argument('--algorithm', type=str, default='nearest_neighbor',
            help='Select interpolation algorithm (nearest_neighbor, linear)')
    parser.add_argument('--offset', type=int, default=0,
            help='Offset between camera timestamp and GPS timestamp in milliseconds (default = 0). ' + \
                 'Positive value means camera timestamp ahead of GPS timestamp.' +\
                 'Only works when --absolute is enabled.')
    parser.add_argument('--absolute', action='store_true', default=False,
            help='Use absolute timestamps for images (default: time relative to first image time.')
    parser.add_argument('--header', action='store_true', default=False,
            help='Add header information to the output file.')
    parser.add_argument('--extension', type=str, default=None,
            help='Append a custom file extension to the image filenames in output file.')
    args = parser.parse_args()

    # Get image filenames
    images = get_images(args.source)
    logging.info('Georeferencing Report')
    logging.info('Created: %s' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    logging.info('Arguments: %s', str(args))
    logging.info('Found %d images in %s' % (len(images), args.source))

    # Get log file from source directory if not explicitly given
    if not args.logfile:
        logfile = get_logfile(args.source)
    else:
        logfile = args.logfile

    # Parse the log file
    logfile_type = get_logfile_type(logfile)
    if logfile_type == 'APM':
        # Read Pose data from APM log file
        pose_info = parse_apm_log_file(logfile)
        logging.info('Found %d camera pose entries in "%s".' % (len(pose_info), logfile))

        # Apply to APM version 2.76+ only
        if get_apm_version(logfile) >= 2.76:
            # Check if timestamps of starting image and starting pose_info 
            # are within a threshold error
            error = images[0].timestamp() - pose_info[0].timestamp() + args.offset
            logging.info('Difference between initial image and pose time: %d ' % error)
            if  error > image_cam_time_threshold:
                logging.error('Difference between initial image and CAM entry time is too large')
                exit(1)

    # Georeference images
    logging.info('Georeferencing images ...')
    georef_images = georeference_images(images, pose_info, args.offset, 
        args.algorithm, args.analyze, args.absolute)

    # Generate Pix4UAV File
    logging.info('Creating Pix4UAV file...')
    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = args.source
    output_filename = args.output

    output_file = output_dir + '/' + output_filename
    gen_pix4uav_file(georef_images, output_file, exclude_imu=args.exclude_imu, 
            header=args.header, ext=args.extension)

    logging.info('Done.')


