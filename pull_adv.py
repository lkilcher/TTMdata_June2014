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

    def checkhash(self, ):
        if self.hash is None:
            return True
        return self.hash == sha(self.fname)


mhkdr = 'https://mhkdr.openei.org/files/'
# (fname, url, filesize, hash)
FILEINFO = [
    Finf('ADV/ttm01_ADVtop_NREL02_June2014.vec',
         mhkdr + '50/ttm01_ADVtop_NREL02_June2014.vec',
         247559612, 'df5d15e92c6c2d5b'),

    Finf('ADV/ttm01_ADVbot_NREL01_June2014.vec',
         mhkdr + '50/ttm01_ADVbottom_NREL01_June2014.vec',
         247977218, 'c1fd5448b155ea7f'),

    Finf('ADV/ttm01b_ADVtop_NREL02_June2014.vec',
         mhkdr + '50/ttm01b_ADVtop_NREL02_June2014.vec',
         321388010, 'c639b458ae3055a2'),

    Finf('ADV/ttm01b_ADVbot_NREL01_June2014.vec',
         mhkdr + '50/ttm01b_ADVbottom_NREL01_June2014.vec',
         327756366, '3117987dd5840e58'),

    Finf('ADV/ttm02b_ADVtop_NREL03_June2014.vec',
         mhkdr + '50/ttm02b_ADVtop_NREL03_June2014.vec',
         318368731, '5801641c827d5991'),

    Finf('ADV/ttm02b_ADVbot_F01_June2014.vec',
         mhkdr + '50/ttm02b_ADVbottom_F01_June2014.vec',
         316418997, 'b77e4040ab77b4e3'),
]


def checkfile(finf, ):
    if not path.isfile(finf.fname):
        return False
    if not path.getsize(finf.fname) == finf.size:
        print("Size of local file '{}' is wrong. Redownloading..."
              .format(finf.fname))
        return False
    if not finf.checkhash():
        print("Secure hash of local file '{}' is wrong. Redownloading..."
              .format(finf.fname))
        return False
    return True


def retrieve(finf):
    response = urlopen(finf.url)
    with open(thisdir + '/' + finf.fname, 'wb') as f:
        shutil.copyfileobj(response, f)


def main(test_only=False):
    for finf in FILEINFO:
        if not checkfile(finf):
            if test_only:
                continue
            print("Downloading '{}'... ".format(finf.fname), end='')
            retrieve(finf)
            if not finf.checkhash():
                raise Exception('Secure hash check failed!')
            print("Done.")
        else:
            print("File '{}' already exists.".format(finf.fname))


if __name__ == '__main__':
    main()
