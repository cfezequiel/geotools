'''
GIS file formats

@author: Carlos Ezequiel

'''

from os import path

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

class MMTile:
    '''Micromappers tile format for JSON conversion.'''

    def __init__(self, north, east, west, south, imgwidth, imgheight, base_url, filename):
        self.data = {'bounds': [east, north, west, south], 'size': [imgwidth, imgheight], 
                     'url':base_url + '/' + path.basename(filename)}

        
