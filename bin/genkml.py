#! /usr/bin/python

'''
Generates a KML file from another GIS file (i.e. APM, Pix4UAV, etc.)

author: Carlos F. Ezequiel
version: 1.0
'''

import re
import argparse
import csv
from os import path

# Third-party modules
from lxml import etree
from pykml.factory import KML_ElementMaker as KML

color = {'blue':'7fffff00', 'light_green':'7f73fb76', 'yellow':'7f00ff00'}

def CDATA(s):
    '''Encapsulate string in CDATA tag.'''

    # FIXME: how to use this with 'Description' tag?
    #cdata = etree.CDATA(s)

    cdata = '<![CDATA[%s]]>' % s

    return cdata

def check_filetype(filename):

    ext = path.splitext(filename)[1]
    if ext == '.log':
        with open(filename, 'rt') as fp:
            if '\n'.join(fp.readlines()).find('CAM') >= 0:
                return 'APM'
    elif ext == '.txt':
        with open(filename, 'rt') as fp:
            reader = csv.reader(fp, delimiter=',')
            row = reader.next()
            if len(row) == 7 or len(row) == 4:
                return 'PIX4UAV'

    return '' 

def read_pix4uav_file(filename):
    '''Read a Pix4UAV file.'''

    fp = open(filename, 'rt')
    reader = csv.reader(fp, delimiter=',')
    data = []
    for row in reader:
        data.append(tuple([s.strip() for s in row]))

    return data
        
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

def read_apm_log_file(filename):

    # Get APM log version
    version = get_apm_log_version(filename)

    # Read APM log file
    fp = open(filename, 'rt')
    data = []
    for line in fp.readlines():
        if line.find('CAM') == 0:
            tokens = [s.strip() for s in line.split(',')]
            if version >= 2.76:
                tokens = tokens[2:]
            else:
                tokens = tokens[1:]
            data.append(tuple(tokens))
            
    return data


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
            description=
            '''
            Convert a Pix4UAV input file into a KML file
            '''
            )
    parser.add_argument('source', type=str, help='Input file')
    args = parser.parse_args()

    # Check type of input file
    filename = args.source
    filetype = check_filetype(filename)
    #assert filetype != '' #DEBUG
    data = []
    if filetype == 'APM':
        data = read_apm_log_file(filename)
    elif filetype == 'PIX4UAV':
        data = read_pix4uav_file(filename)

    # Create KML document
    doc = KML.Document(
            KML.Style(
                KML.LineStyle(
                    KML.color(color['blue']),
                    KML.colorMode('normal'),
                    KML.width('4')
                    ),
                KML.PolyStyle(
                    KML.color(color['light_green'])
                    ),
                id='kml_style'
                )
            )

    path_data = []
    idx = 1;
    for row in data:
        name = row[0]
        lat = row[1]
        lon = row[2]
        alt = row[3]
        path_data.append(','.join([lon, lat, alt]))

        # TODO: elaborate data in description
        if name.find('JPG') >= 0:
            description = CDATA('<img src=%s alt=%s>' % (name, name))
        else:
            description = name

        # Create KML placemark
        pm = KML.Placemark(
                KML.name(str(idx)),
                KML.description(description),
                KML.Point(
                    KML.coordinates('%s, %s, %s' % (lon, lat, alt))
                    )
                )
        doc.append(pm)

        idx += 1

    # Create KML path
    pm_path = KML.Placemark(
                KML.styleUrl('#kml_style'),
                KML.name('Path'),
                KML.LineString(
                    KML.extrude('1'),
                    KML.tessellate('1'),
                    KML.altitudeMode('relative'),
                    KML.coordinates('\n'.join(path_data))
                    )
                )
    doc.append(pm_path)

    # Write KML object to file
    kml = KML.kml(doc)
    xml_str = etree.tostring(kml, pretty_print = True)
    outfp = open(path.splitext(args.source)[0] + '.kml', 'wt')
    outfp.write(xml_str)
    outfp.close()

