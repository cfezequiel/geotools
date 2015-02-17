'''
Transform a world file into a CSV containing grid coordinates

@author: Carlos Ezequiel

'''

import sys
from os import path
import csv

IMG_WIDTH=1000
IMG_HEIGHT=1000

class WorldFile:

    def __init__(self, filename, name=None, imgwidth=0, imgheight=0):
        '''Read worldfile file and parse data '''

        with open(filename, 'rt') as fp:
            self.name = name or filename
            self.xscale = float(fp.readline().strip())
            self.yskew = float(fp.readline().strip())
            self.xskew = float(fp.readline().strip())
            self.yscale = float(fp.readline().strip())
            self.ulx = float(fp.readline().strip())
            self.uly = float(fp.readline().strip())

        # Derived attributes
        # -- Upper right --
        self.urx = self.ulx + self.xscale * imgwidth
        self.ury = self.uly

        # -- Lower right --
        self.lrx = self.ulx + self.xscale * imgwidth
        self.lry = self.uly + self.yscale * imgheight
        
        # -- Lower left --
        self.llx = self.ulx
        self.lly = self.uly + self.yscale * imgheight


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
                writer.writerow([wf.name, 'ul', wf.ulx, wf.uly])
                writer.writerow([wf.name, 'ur', wf.urx, wf.ury])
                writer.writerow([wf.name, 'lr', wf.lrx, wf.lry])
                writer.writerow([wf.name, 'll', wf.llx, wf.lly])




