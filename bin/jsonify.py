'''Generate JSON file from orthomosaic tile image + XML metadata.'''

import sys
from xml.etree import ElementTree as ET
from os import listdir, path 
import json
from PIL import Image

from gistools.crs import utm2dd
from gistools.fmt import WorldFile, MMTile

VALID_FILE_EXT = ['.JPG']

# PARAMETERS
BASE_URL = 'https://s3-ap-southeast-1.amazonaws.com/'
ZONE = 51
IS_NORTH = True

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print 'Usage: python %s <.JPG+.JGw directory> <AWS s3 path>>' % path.basename(sys.argv[0])
        print 'Current AWS URL: %s' % BASE_URL
        exit(1)

    url = BASE_URL + sys.argv[2]

    src_dir = sys.argv[1]

    # Read input directory images
    tile_image_files = ['%s/%s' % (src_dir, f) for f in listdir(src_dir) \
            if path.splitext(f)[1] in VALID_FILE_EXT]

    # for each file
    tiles = []
    for f in tile_image_files:
        # Get worldfile and extract coordinates
        print 'Processing ', f
        # Get file size
        im = Image.open(f)
        image_size = list(im.size)
        imgwidth = image_size[0]
        imgheight = image_size[1]

        world_file = path.splitext(f)[0] + '.JGw'
        wf = WorldFile(world_file, imgwidth=imgwidth, imgheight=imgheight)
        (north, east) = utm2dd(ZONE, wf.lrx, wf.uly, IS_NORTH)
        (south, west) = utm2dd(ZONE, wf.ulx, wf.lly, IS_NORTH)

        tile = MMTile(north, east, west, south, imgwidth, imgheight, url, f)

        # Create JSON entry
        tiles.append(tile.data)

    # Create JSON file
    with open('output.json', 'wt') as fp:
       fp.write(json.dumps(tiles, sort_keys=True, indent=4))

    print '%d tile_image_files processed' % len(tile_image_files)

