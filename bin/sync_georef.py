'''
Filter georeferencing CSV file to take out entries that do not
have matching image files.
'''

import os
import csv
import argparse
import shutil

def isTIFF(filename):
    if filename.find('.tiff') >= 0 or filename.find('.tif') >= 0:
        return True

    return False
    

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("src", help="Source directory")
    args = parser.parse_args()

    assert os.path.isdir(args.src)

    for root, dirs, files in os.walk(args.src):
        print 'Checking ' + root
        for f in files:
            if f == 'georef.csv':
                print 'Found CSV. Looking for TIFF images'
                try:
                    dir_ = root + '/../TIFF'
                    images = [img for img in os.listdir(dir_) if isTIFF(img) == True]
                except:
                    print 'Could not find TIFF directory for CSV @ ' + root
                    break
                csvfp = open(root + '/' + f, 'rtU')
                reader = csv.reader(csvfp, delimiter=',')
                header = reader.next()
                rows = []
                for row in reader:
                    rows.append(row)
                out_rows = []
                csv_filter_count = 0
                for row in rows:
                    if row[0] in images:
                        out_rows.append(row)
                    else:
                        print 'In %s: Filtering out %s' % (f, row[0])
                        csv_filter_count += 1

                row_names = [r[0] for r in rows]
                reject_dir = dir_ + '/.reject'
                if not os.path.exists(reject_dir):
                    os.mkdir(reject_dir)
                img_filter_count = 0
                for img in images:
                    if img not in row_names:
                        print 'Filtering out %s from %s' % (img, dir_)
                        shutil.move(dir_ + '/' + img, reject_dir)
                        img_filter_count += 1

                print 'Filtered out %d entries from %s' % (csv_filter_count, f)
                print 'Filtered out %d files from %s' % (img_filter_count, dir_)
                filename = dir_ + '/' + root.split('/')[-2] + '_georef_filtered.csv'
                print 'Writing filtered csv: %s' % filename
                writer = csv.writer(open(filename, 'wt'), delimiter=',')
                writer.writerow(header)
                for row in out_rows:
                    writer.writerow(row)
                break

