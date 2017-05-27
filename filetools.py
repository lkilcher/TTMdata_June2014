import hashlib
import shutil
import os.path as path
try:
    from urllib.request import urlopen
except:
    from urllib import urlopen

pkg_root = path.dirname(path.realpath(__file__)) + '/'


def sha(fname):
    h = hashlib.sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


class Finf(object):

    def __init__(self, source_fname, url, size, hash=None):
        self.source_fname = source_fname
        self.url = url
        self.size = size
        self.hash = hash

    def __repr__(self, ):
        return '<Finf object: {}>'.format(self.fname)

    def checkhash(self, ):
        if self.hash is None:
            return True
        return self.hash == sha(self.abs_source_fname)

    def checkfile(self, ):
        if not path.isfile(self.abs_source_fname):
            return None
        if not path.getsize(self.abs_source_fname) == self.size:
            print("Size of local file '{}' is wrong."
                  .format(self.source_fname))
            return False
        if not self.checkhash():
            print("Secure hash of local file '{}' is wrong."
                  .format(self.source_fname))
            return False
        return True

    @property
    def fname(self, ):
        out = self.source_fname
        for ending in ['.vec', '.VEC', '.wpr', '.WPR']:
            out = out.rstrip(ending)
        return out

    @property
    def abs_fname(self, ):
        return pkg_root + self.fname

    @property
    def abs_source_fname(self, ):
        return pkg_root + self.source_fname


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
    with open(finf.abs_source_fname, 'wb') as f:
        shutil.copyfileobj(response, f)
    print("Done.")
