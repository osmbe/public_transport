#!/bin/python
# -*- coding: utf-8 -*-
import os, sys, re, zipfile, ftplib
zipre = re.compile('\d\d\d\d-\d\d-\d\d\.zip$')

cwd = os.getcwd()
wd = cwd + r'/data/DL'

""" Fetch the latest zip file from the ftp site of De Lijn """

class Callback(object):
    '''This prints a nice progress status on the command line'''
    def __init__(self, totalsize, fp):
        self.totalsize = totalsize
        self.fp = fp
        self.received = 0

    def __call__(self, data):
        self.fp.write(data)
        self.received += len(data)
        print('\r%i%% complete' % (100.0*self.received/self.totalsize), end='\r')

print ('Reading credentials from "credentials.txt"')
with open("credentials.txt") as credentials:
    l = list(credentials)
    username = l[0] #.readlines()
    password = l[1] #.readlines()

ftp=ftplib.FTP(host='poseidon.delijn.be', user=username, passwd=password)
ftp.cwd('current')
print ("Get name of newest file")
fn = ftp.nlst()[0]
localfn = wd + '/' + fn
print('Saving to ' + fn)
size = ftp.size(fn)
if not(fn in os.listdir(wd)):
    # Only download if a newer file is available
    print (fn + " found, downloading latest version of De Lijndata")
    with open(localfn, 'wb') as fh:
        w = Callback(size, fh)
        ftp.retrbinary('RETR %s' % fn, w, 32768)

    ftp.quit()
else:
    print('Latest version ' + fn + ' already present, nothing to do')
    exit(1)

""" Unzip the latest file we have available in the current directory """

files = os.listdir(path=wd)
zipfn=''
for file in files:
    if re.match(zipre, file):
        if file > zipfn:
            zipfn = wd + '/' + file

zfile = zipfile.ZipFile(zipfn)
print(); print(); print("Found " + zipfn)
for name in zfile.namelist():
    """Recode csv-file with textual content to UTF-8 """
    (dirname, filename) = os.path.split(name)
    print("Decompressing " + filename)
    fd = open('data/' + name,"wb")
    fd.write(zfile.read(name).decode('latin-1').replace('\r','').replace('"','').encode('utf-8'))
    fd.close()

print ('All files unzipped')
