import warnings
import time
from os.path import getmtime
import datetime

# Try importing dependencies
has_exifread = False
has_exiftool = False

try:
    import exifread
    has_exifread = True
except ImportError:
    warnings.warn('Module not found: exifread')

try:
    import exiftool
    has_exiftool = True
except ImportError:
    warnings.warn('Module not found: exiftool')

# Leap seconds between UTC and GPS times
LEAP_SECONDS = 16
UNIX_EPOCH = datetime.date(1970,1,1)
GPS_EPOCH= datetime.date(1980,1,6)
EPOCH_DIFF= GPS_EPOCH - UNIX_EPOCH
UNIX_GPS_OFFSET_S = EPOCH_DIFF.days*24*3600+EPOCH_DIFF.seconds
SECONDS_PER_DAY = 86400
DAYS_PER_WEEK = 7
SECONDS_PER_WEEK = SECONDS_PER_DAY * DAYS_PER_WEEK

def gps_time_to_seconds(gps_week, gps_seconds):
    '''
    Convert GPS time (GPSWeek, GPSSeconds) to seconds since Unix epoch
    '''

    days = float(gps_seconds) / SECONDS_PER_DAY 
    daysIntoWeek = float(days) / DAYS_PER_WEEK 

    weeks = gps_week + daysIntoWeek
    seconds = weeks * SECONDS_PER_WEEK + UNIX_GPS_OFFSET_S

    return seconds

def get_timestamp(filename):
    '''Get file creation time from EXIF if available. If not, get file modified time.'''

    # Extract date time
    date_time_original = None
    if has_exifread:
        tags = exifread.process_file(open(filename, 'rt'))
        try:
            date_time_original = str(tags['EXIF DateTimeOriginal'])
        except KeyError:
            if has_exiftool:
                with exiftool.ExifTool() as et:
                    md = et.get_metadata(filename)
                    try:
                        date_time_original = str(md['EXIF:DateTimeOriginal'])
                    except KeyError:
                        pass # do nothing

            else:
                pass # do nothing at this point
    
    # Convert to a time object
    if date_time_original:
        fmt = '%Y:%m:%d %H:%M:%S'
        t = time.strptime(date_time_original, fmt)
    else: # Use the image file's modified time instead
        warnings.warn('Using modified time of image file %s' %  filename)
        t = time.localtime(getmtime(filename))

    return t

def gps_seconds(t):
    '''Convert time object to GPS seconds.

    NOTE: GPS seconds referenced from start of the week
    
    '''

    gps_s = (t.tm_wday + 1) % 7 * 24 * 60 * 60 + t.tm_hour * 60 * 60 + t.tm_min * 60 + t.tm_sec
    gps_s += time.timezone + LEAP_SECONDS

    return gps_s


