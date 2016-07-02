# geotools

* Python tools for extracting information from geospatial images and metadata
* Version 0.8

## Install

From root directory, type
```
$ python setup.py install
```
- You should have Python 2.7.x installed on your machine
    - To check, type `python -V`

The bin/ scripts should now be accessible in your $PATH.


## Scripts

Executable scripts can be found in `bin/`

- jsonify.py: Generate JSON file from orthomosaic tile image + XML metadata.
- genkml.py: Generates a KML file from another GIS file (i.e. APM, Pix4UAV, etc.).
- georef.py: Georeferences a set of images with GPS/IMU information. Interpolates for images missing matching GPS timestamp data
- georefvid.py: Georeferences GoPro video-based frames.
- obliquelabel.py: Label entries of a georeferencing CSV file to determine whether image is oblique (i.e. non-orthogonal) or not.
- wf2grid.py: Transform world file into a CSV containing filename and grid coordinates.
