#!/usr/bin/python
from __future__ import print_function
try:
    from urllib.request import urlopen
except:
    from urllib import urlopen

import os.path as path
import shutil
import hashlib


try:
    thisdir = path.dirname(path.realpath(__file__))
except NameError:
    thisdir = './'


def sha(fname):
    h = hashlib.sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


class Finf(object):

    def __init__(self, fname, url, size, hash=None):
        self.fname = fname
        self.url = url
        self.size = size
        self.hash = hash

    def __repr__(self, ):
        return '<Finf object: {}>'.format(self.fname)

    def checkhash(self, ):
        if self.hash is None:
            return True
        return self.hash == sha(self.fname)

    def checkfile(self, ):
        if not path.isfile(self.fname):
            return None
        if not path.getsize(self.fname) == self.size:
            print("Size of local file '{}' is wrong."
                  .format(self.fname))
            return False
        if not self.checkhash():
            print("Secure hash of local file '{}' is wrong."
                  .format(self.fname))
            return False
        return True


mhkdr = 'https://mhkdr.openei.org/files/'
# (fname, url, filesize, hash)
FILEINFO = {
    'ttm01-top':
    Finf('ADV/ttm01_ADVtop_NREL02_June2014.vec',
         mhkdr + '50/ttm01_ADVtop_NREL02_June2014.vec',
         247559612, 'df5d15e92c6c2d5b'),
    'ttm01-bot':
    Finf('ADV/ttm01_ADVbot_NREL01_June2014.vec',
         mhkdr + '50/ttm01_ADVbottom_NREL01_June2014.vec',
         247977218, 'c1fd5448b155ea7f'),
    'ttm01b-top':
    Finf('ADV/ttm01b_ADVtop_NREL02_June2014.vec',
         mhkdr + '50/ttm01b_ADVtop_NREL02_June2014.vec',
         321388010, 'c639b458ae3055a2'),
    'ttm01b-bot':
    Finf('ADV/ttm01b_ADVbot_NREL01_June2014.vec',
         mhkdr + '50/ttm01b_ADVbottom_NREL01_June2014.vec',
         327756366, '3117987dd5840e58'),
    'ttm02b-top':
    Finf('ADV/ttm02b_ADVtop_NREL03_June2014.vec',
         mhkdr + '50/ttm02b_ADVtop_NREL03_June2014.vec',
         318368731, '5801641c827d5991'),
    'ttm02b-bot':
    Finf('ADV/ttm02b_ADVbot_F01_June2014.vec',
         mhkdr + '50/ttm02b_ADVbottom_F01_June2014.vec',
         316418997, 'b77e4040ab77b4e3'),
}


def retrieve(finf):
    print("Retrieving file {}...".format(finf.fname))
    retval = finf.checkfile()
    if retval:
        print("  File exists, hash check passed.")
        return
    elif retval is None:
        print("  Downloading...")
    elif retval is False:
        print("  hash check failed, redownloading...")
    response = urlopen(finf.url)
    with open(thisdir + '/' + finf.fname, 'wb') as f:
        shutil.copyfileobj(response, f)
    print("Done.")


def main(files_info=FILEINFO.values(), test_only=False):
    for finf in files_info:
        retrieve(finf)

if __name__ == '__main__':
    main()
