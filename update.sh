#! /bin/bash

#FIXME: this doesn't work for some reason
TARGET='/home/carlos/network/SFTP\ on\ se-server00.local/mnt/SE-DATASTORE/DATASET/SOFTWARE/Scripts'

rsync apm_to_pix4uav/apm2pix4uav.py /home/carlos/network/SFTP\ on\ se-server00.local/mnt/SE-DATASTORE/DATASET/SOFTWARE/Scripts/
rsync genkml/genkml.py /home/carlos/network/SFTP\ on\ se-server00.local/mnt/SE-DATASTORE/DATASET/SOFTWARE/Scripts/
#cp genkml/genkml.py ${TARGET}
