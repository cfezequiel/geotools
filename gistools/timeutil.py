import warnings
import time

# Leap seconds between UTC and GPS times
LEAP_SECONDS = 16

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

def get_timestamp(filename):
    '''Get file creation time from EXIF if available. If not, get file modified time.'''

    # Extract date time
    date_time_original = None
    if has_exifread:
        tags = exifread.process_file(open(filename, 'rt'))
        if tags:
            date_time_original = str(tags['EXIF DateTimeOriginal'])
        else:
            if has_exiftool:
                with exiftool.ExifTool() as et:
                    md = et.get_metadata(filename)
                    date_time_original = str(md['EXIF:DateTimeOriginal'])
            else:
                pass # do nothing at this point
    
    # Convert to a time object
    if date_time_original:
        fmt = '%Y:%m:%d %H:%M:%S'
        t = time.strptime(date_time_original, fmt)
    else: # Use the image file's modified time instead
        t = time.localtime(path.getmtime(filename))

    return t

def gps_seconds(t):
    '''Convert time object to GPS seconds.

    NOTE: GPS seconds referenced from start of the week
    
    '''

    gps_s = (t.tm_wday + 1) % 7 * 24 * 60 * 60 + t.tm_hour * 60 * 60 + t.tm_min * 60 + t.tm_sec
    gps_s += time.timezone + LEAP_SECONDS

    return gps_s


