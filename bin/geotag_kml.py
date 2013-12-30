#! /usr/bin/python

import sys
from os import path, listdir
import csv
import argparse
from cStringIO import StringIO

from lxml import etree
from pykml.factory import KML_ElementMaker as KML
from pykml.factory import ATOM_ElementMaker as ATOM
from pykml.factory import GX_ElementMaker as GX

DEBUG = False
IMAGE_DIR = 'images'

def CDATA(s):
    '''Encapsulate string in CDATA tag.'''

    # FIXME: how to use this with 'Description' tag?
    #cdata = etree.CDATA(s)

    cdata = '<![CDATA[%s]]>' % s

    return cdata

def fix_special_char(s):
    '''Fix special characters that were replaced due to XML serialization.'''

    s = s.replace('&lt;', '<')
    s = s.replace('&gt;', '>')
    return s

def csv2kml(csvfile, name='output.kml'):
    '''Convert CSV file of geotagged images to KML file.'''

    # Parse CSV file
    reader = csv.reader(csvfile, delimiter=',')

    # Form KML document 
    doc = KML.Document(KML.name(name))

    # Add placemarks to KML document 
    if DEBUG:
        debug_count = 2 #DEBUG
    for row in reader:
        # Ignore header data
        if row[0] == 'Time':
            continue
        name = row[1]
        marker = row[2]
        lat = row[3]
        lon = row[4]
        alt = 0

        #TODO: add different colored placemarks depending on marker type

        pm = KML.Placemark(
          KML.name(path.splitext(name)[0]),
          KML.description(CDATA('<img src=%s/%s>' % (IMAGE_DIR, name))),
          KML.Point(
            GX.drawOrder('1'),
            KML.coordinates('%s,%s,%s' % (lon, lat, alt)),
          )
        )

        doc.append(pm)

        if DEBUG:
            debug_count -= 1
            if not debug_count:
                break

    kml = KML.kml(doc)

    # Close CSV file
    csvfile.close()

    # Return KML object 
    return kml


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Generates KML file from CSV/s')
    parser.add_argument('source', type=str, help='CSV file or directory containing CSVs')
    parser.add_argument('-o', '--output', default='output.kml', type=str, 
            help='Output KML filename [default: output.kml]')
    args = parser.parse_args()

    assert path.exists(args.source)

    if path.isdir(args.source):
        csv_dir = args.source
        csv_files = ['%s/%s' % (csv_dir, f) for f in listdir(csv_dir) if f.endswith('.csv')]
        csv_str = ''
        for f in csv_files:
            fp = open(f, 'rb')
            csv_str += fp.read() + '\n'
        csvfile = StringIO(csv_str)

    elif path.isfile(args.source):
        csvfile = open(args.source, 'rb')

    # Convert to KML
    kml = csv2kml(csvfile, name=args.output)

    # Create KML string
    kml_str = etree.tostring(kml, pretty_print=True)

    # Fix special characters
    kml_str = fix_special_char(kml_str)

    # Write KML file
    fp = open(args.output, 'wb')
    fp.write(kml_str)
    fp.close()


