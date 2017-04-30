from __future__ import print_function
try:
    from urllib.request import urlopen
except:
    from urllib import urlopen

import os.path as path
import shutil


class Finf(object):

    def __init__(self, fname, url, size):
        self.fname = fname
        self.url = url
        self.size = size

mhkdr = 'https://mhkdr.openei.org/files/'
# {fname: (url, filesize)}
FILEINFO = [
    Finf('ADV/ttm01_ADVtop_NREL02_June2014.vec',
         mhkdr + '50/ttm01_ADVtop_NREL02_June2014.vec',
         247559612),
    Finf('ADV/ttm01_ADVbot_NREL01_June2014.vec',
         mhkdr + '50/ttm01_ADVbottom_NREL01_June2014.vec',
         247977218),
    Finf('ADV/ttm01b_ADVtop_NREL02_June2014.vec',
         mhkdr + '50/ttm01b_ADVtop_NREL02_June2014.vec',
         321388010),
    Finf('ADV/ttm01b_ADVbot_NREL01_June2014.vec',
         mhkdr + '50/ttm01b_ADVbottom_NREL01_June2014.vec',
         327756366),
    Finf('ADV/ttm02b_ADVtop_NREL03_June2014.vec',
         mhkdr + '50/ttm02b_ADVtop_NREL03_June2014.vec',
         318368731),
    Finf('ADV/ttm02b_ADVbot_F01_June2014.vec',
         mhkdr + '50/ttm02b_ADVbottom_F01_June2014.vec',
         316418997),
]

try:
    thisdir = path.dirname(path.realpath(__file__))
except NameError:
    thisdir = './'


def checkfile(finf, ):
    if not path.isfile(finf.fname):
        return False
    if not path.getsize(finf.fname) == finf.size:
        print("Size of local file '{}' is wrong. Redownloading..."
              .format(finf.fname))
        return False
    print("File '{}' already exists.".format(finf.fname))
    return True


def retrieve(finf, show_progress=True):
    response = urlopen(finf.url)
    with open(thisdir + '/' + finf.name, 'wb') as f:
        shutil.copyfileobj(response, f)


def main():
    for finf in FILEINFO:
        if not checkfile(finf):
            print("Downloading '{}'... ".format(finf.fname), end='')
            retrieve(finf.url, finf.fname)
            print("Done.")

if __name__ == '__main__':
    main()
