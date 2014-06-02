#! /usr/bin/python

'''
Label entries of a georef CSV file to determine whether image
is oblique or not.
'''

import argparse
import os
import csv
import codecs

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("csvfn", help="CSV file")
    parser.add_argument("rejectfn", help="Reject file")
    parser.add_argument('-o', help='Destination directory')

    args = parser.parse_args()

    with open(args.csvfn, "rb") as csvfile:
        rejected = []
        with codecs.open(args.rejectfn, 'rU', 'utf=16') as rejectfile:
            reject_rd = csv.reader(rejectfile, delimiter='\t')
            reject_rd.next()
            for row in reject_rd:
                name = row[0]
                name = os.path.splitext(name)[0]
                rejected.append(name)
        csvreader = csv.reader(csvfile, delimiter=',')

        if not args.o:
            outfn = '_label'.join(os.path.splitext(args.csvfn))
        else:
            outfn = args.o

        with open(outfn, 'wt') as outfile:
            writer = csv.writer(outfile, delimiter=',')
            writer.writerow(csvreader.next() + ['IsOblique'])
            for row in csvreader:
                name = os.path.splitext(row[0])[0]
                if name in rejected:
                    label = 1
                else:
                    label = 0
                writer.writerow(row + [label])



