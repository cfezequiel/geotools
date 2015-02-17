'''
Transform a world file into a CSV containing filename and grid coordinates

@author: Carlos Ezequiel

'''

import sys
from os import path
import csv

from gistools import crs
from gistools.fmt import WorldFile

IMG_WIDTH=1000
IMG_HEIGHT=1000
ZONE=51
NORTH=True

if __name__ == '__main__':

    if len(sys.argv) < 2:
        app = path.basename(sys.argv[0])
        print 'Usage: %s <text file containing files to process>' % app
        exit(1)
    
    filelist = sys.argv[1]
    with open(filelist, 'rt') as fp:
        with open('output.csv', 'wt') as fpw:
            writer = csv.writer(fpw, delimiter=',')
            for f in iter(fp.readlines()):
                wf = WorldFile(f.strip(), None, IMG_WIDTH, IMG_HEIGHT)
                (ulx, uly) = crs.utm2dd(ZONE, wf.ulx, wf.uly, NORTH)
                (urx, ury) = crs.utm2dd(ZONE, wf.ulx, wf.uly, NORTH)
                (lrx, lry) = crs.utm2dd(ZONE, wf.ulx, wf.uly, NORTH)
                (llx, lly) = crs.utm2dd(ZONE, wf.ulx, wf.uly, NORTH)
                
                writer.writerow([wf.name, 'ul', ulx, uly])
                writer.writerow([wf.name, 'ur', urx, ury])
                writer.writerow([wf.name, 'lr', lrx, lry])
                writer.writerow([wf.name, 'll', llx, lly])




