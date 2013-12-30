import subprocess
import os

prog = 'python ~/Dropbox/Tools/apm2pix4uav.py'
args = prog + ' --algorithm=linear ' + root + ' -d ' + root 

if __name__ == '__main__':

    hasLog = False
    hasImg = False
    for root, dirs, files in os.walk('.'):
        for f in files:
            if f.find('.log') >= 0:
                hasLog = True
            elif f.find('.jpg') >= 0:
                hasImg = True

        if hasLog and hasImg:
            print 'Processing dir: %s' % root
            print 'Command: %s' % args
            subprocess.call(args, shell=True)
            hasLog = False
            hasImg = False

