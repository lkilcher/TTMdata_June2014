from __future__ import print_function
try:
    from urllib.request import urlopen
except:
    from urllib import urlopen

import os.path as path
import shutil


URLS = [
    'https://mhkdr.openei.org/files/50/ttm01_ADVtop_NREL02_June2014.vec',
    'https://mhkdr.openei.org/files/50/ttm01_ADVbottom_NREL01_June2014.vec',
    'https://mhkdr.openei.org/files/50/ttm01b_ADVtop_NREL02_June2014.vec',
    'https://mhkdr.openei.org/files/50/ttm01b_ADVbottom_NREL01_June2014.vec',
    'https://mhkdr.openei.org/files/50/ttm02b_ADVtop_NREL03_June2014.vec',
    'https://mhkdr.openei.org/files/50/ttm02b_ADVbottom_F01_June2014.vec',
]
sizes = {
    'ttm01_ADVtop_NREL02_June2014.vec': 247559612,
    'ttm01_ADVbot_NREL01_June2014.vec': 247977218,
    'ttm01b_ADVtop_NREL02_June2014.vec': 321388010,
    'ttm01b_ADVbot_NREL01_June2014.vec': 327756366,
    'ttm02b_ADVtop_NREL03_June2014.vec': 318368731,
    'ttm02b_ADVbot_F01_June2014.vec': 316418997,
]

try:
    thisdir = path.dirname(path.realpath(__file__))
except NameError:
    thisdir = './'


def checkfile(fname, ):
    if not path.isfile(fname):
        return False
    if not path.getsize(fname) == sizes[fname]:
        print("Size of {} is wrong. Redownloading...".format(fname))
        return False
    print("File '{}' already exists.".format(fname))
    return True


def retrieve(url, name, show_progress=True):
    response = urlopen(url)
    with open(thisdir + '/' + name, 'wb') as f:
        shutil.copyfileobj(response, f)


def main():
    for url in URLS:
        fname = 'ADV/' + url.rsplit('/', 1)[-1].replace('bottom', 'bot')
        if not checkfile:
            print("Downloading '{}'... ".format(fname), end='')
            retrieve(url, fname)
            print("Done.")

if __name__ == '__main__':
    main()
