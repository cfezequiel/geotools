from setuptools import setup

setup(name='gistools',
      version='0.3',
      description='Collection of GIS utility scripts and modules',
      url='http://TODO/this/later',
      author='Carlos Ezequiel',
      author_email='carlosezequiel@skyeyeproject.com',
      license='MIT',
      packages=['gistools'],
      scripts=['bin/georef.py', 'bin/genkml.py', 'bin/label.py', 'bin/georef_vid.py'],
      zip_safe=False)
