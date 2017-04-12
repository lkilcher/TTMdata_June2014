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

try:
    thisdir = path.dirname(path.realpath(__file__))
except NameError:
    thisdir = './'


def retrieve(url, name, show_progress=True):
    response = urlopen(url)
    with open(thisdir + '/' + name, 'wb') as f:
        shutil.copyfileobj(response, f)


def main():
    for url in URLS:
        fname = url.rsplit('/', 1)[-1]
        if not path.isfile(fname):
            print("Downloading '{}'... ".format(fname), end='')
            retrieve(url, fname)
            print("Done.")
        else:
            print("File '{}' already exists.".format(fname))

if __name__ == '__main__':
    main()
