#! /usr/bin/python

'''
Converts an Pix4UAV file to a KML file for viewing of image geotag locations
'''

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

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
            description=
            '''
            Convert a Pix4UAV input file into a KML file
            '''
            )
    parser.add_argument('source', type=str, help='Pix4UAV file')
    args = parser.parse_args()

    # Read Pix4UAV file
    fp = open(args.source, 'rt')
    reader = csv.reader(fp, delimiter=',')

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
    img_idx = 1;
    for row in reader:
        image_name = row[0]
        lat = row[1]
        lon = row[2]
        alt = row[3]
        path_data.append(','.join([lon, lat, alt]))

        # Create KML placemark
        pm = KML.Placemark(
                KML.name(str(img_idx)),
                KML.description(CDATA('<img src=%s alt=%s>' % (image_name, image_name))),
                KML.Point(
                    KML.coordinates('%s, %s, %s' % (lon, lat, alt))
                    )
                )
        doc.append(pm)

        img_idx += 1

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

