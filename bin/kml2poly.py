#! /usr/bin/python

from os import path
import argparse

from pykml import parser as kmlparser

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
            description=
            '''
            Extract polygon objects from KML file for use in APM Mission Planner
            '''
            )
    parser.add_argument('src', type=str, help='Source file')
    parser.add_argument('-p', '--output_fmt',
            help='Output .poly file [default: output_%%03d]')
    args = parser.parse_args()

    # Check args
    assert path.exists(args.src)
    assert path.isfile(args.src)

    p = kmlparser.parse(open(args.src, 'rb')) 
    root = p.getroot()

    # Get all placemarks
    placemarks = root.findall('.//kml:Placemark', namespaces=root.nsmap)

    # Write placemark coordinates to poly file
    index = 1
    for pm in placemarks:
        # Get coordinates for valid Placemarks; skip if not valid
        el = pm.find('.//kml:LineString', namespaces=root.nsmap) or \
             pm.find('.//kml:Polygon', namespaces=root.nsmap)
        if el is None:
            continue
        coordinates = str(el.find('.//kml:coordinates', namespaces=root.nsmap)).split(' ')

        # Set output format
        if args.output_fmt:
            outfile = args.output_fmt % index + '.poly'
            index += 1
        elif pm.name:
            outfile = (str(pm.name) + '.poly').replace(' ', '_')
        else:
            outfile = 'output%03d.poly' % index
            index += 1

        # Write coordinates to poly file
        with open(outfile, 'wb') as outfp:
            outfp.write('#saved by %s\n' % parser.prog)
            for c in coordinates:
                c = c.strip()
                if not c:
                    continue
                (lon, lat, alt) = c.split(',')
                outfp.write('%s %s\n' % (lat, lon))


