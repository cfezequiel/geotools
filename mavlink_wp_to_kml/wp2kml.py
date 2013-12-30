#! /Users/carlos/anaconda/bin/python

import sys
import os

from pykml.factory import KML_ElementMaker as KML
from lxml import etree

if __name__ == '__main__':
    '''Convert MAVLink waypoint file to KML file'''

    if len(sys.argv) < 2:
        print 'Usage: %s <waypoint file>'
        exit(1)

    filename = sys.argv[1]

    inFile = open(filename, 'rt')
    lines = inFile.readlines()
    inFile.close()

    outFilename = os.path.splitext(filename)[0] + '.kml'
    doc = KML.Document()
    for line in lines:
        print line
        # Skip empty and header lines
        if line.isspace() or line.find('QGC') >= 0:
            continue

        lineData = line.split()
        wpIndex = int(lineData[0])
        wpLat = float(lineData[8])
        wpLon = float(lineData[9])

        pm = KML.Placemark(
                KML.name(wpIndex),
                KML.Point(
                    KML.coordinates("%s, %s" % (wpLon, wpLat))
                    )
                )

        doc.append(pm)

    kml = KML.kml(doc)
    xmlString = etree.tostring(kml)
    outFile = open(outFilename, 'wt')
    outFile.write(xmlString)
    outFile.close()

