'''Generate JSON file from orthomosaic tile image + XML metadata.'''

import sys
from xml.etree import ElementTree as ET
from os import listdir, path 
import json
from PIL import Image

VALID_FILE_EXT = ['.JPG']
URL_BASE = 'https://s3-ap-southeast-1.amazonaws.com/skyeye-multiform/micromappers-sample2'

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print 'Usage: python %s <image+xml directory>' % path.basename(sys.argv[0])
        exit(1)

    src_dir = sys.argv[1]

    # Read input directory images
    files = ['%s/%s' % (src_dir, f) for f in listdir(src_dir) \
            if path.splitext(f)[1] in VALID_FILE_EXT]

    # for each file
    samples = []
    for f in files:
        # Get xml and extract metadata
        print 'Processing ', f
        tree = ET.parse(f + '.xml')
        root = tree.getroot()
        e = root.find('dataIdInfo').find('dataExt').find('geoEle').find('GeoBndBox')
        west = e.find('westBL').text
        east = e.find('eastBL').text
        north = e.find('northBL').text
        south = e.find('southBL').text

        # Get file size
        im = Image.open(f)
        image_size = list(im.size)

        # Create JSON entry
        sample = {'bounds': [east, north, west, south], 'size': image_size, 
                'url':URL_BASE + '/' + path.basename(f)}
        samples.append(sample)

    # Create JSON file
    with open('data.json', 'wt') as fp:
       fp.write(json.dumps(samples, sort_keys=True, indent=4))

    print '%d files processed' % len(files)

