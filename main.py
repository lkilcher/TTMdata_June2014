import dolfyn.adv.api as avm
import filetools as ftbx

pkg_root = ftbx.pkg_root

_mhkdr = 'https://mhkdr.openei.org/files/'
# (fname, url, filesize, hash)
FILEINFO = {
    'ttm01-top':
    ftbx.Finf('ADV/ttm01_ADVtop_NREL02_June2014.vec',
              _mhkdr + '50/ttm01_ADVtop_NREL02_June2014.vec',
              247559612, 'df5d15e92c6c2d5b'),
    'ttm01-bot':
    ftbx.Finf('ADV/ttm01_ADVbot_NREL01_June2014.vec',
              _mhkdr + '50/ttm01_ADVbottom_NREL01_June2014.vec',
              247977218, 'c1fd5448b155ea7f'),
    'ttm01b-top':
    ftbx.Finf('ADV/ttm01b_ADVtop_NREL02_June2014.vec',
              _mhkdr + '50/ttm01b_ADVtop_NREL02_June2014.vec',
              321388010, 'c639b458ae3055a2'),
    'ttm01b-bot':
    ftbx.Finf('ADV/ttm01b_ADVbot_NREL01_June2014.vec',
              _mhkdr + '50/ttm01b_ADVbottom_NREL01_June2014.vec',
              327756366, '3117987dd5840e58'),
    'ttm02b-top':
    ftbx.Finf('ADV/ttm02b_ADVtop_NREL03_June2014.vec',
              _mhkdr + '50/ttm02b_ADVtop_NREL03_June2014.vec',
              318368731, '5801641c827d5991'),
    'ttm02b-bot':
    ftbx.Finf('ADV/ttm02b_ADVbot_F01_June2014.vec',
              _mhkdr + '50/ttm02b_ADVbottom_F01_June2014.vec',
              316418997, 'b77e4040ab77b4e3'),
}


def load(tag, coordsys='pax', bin=False):
    """Load a data file from this dataset.

    Parameters
    ----------

    tag : string
       The instrument to load. This may be one of:
          ttm01-bot
          ttm01-top
          ttm01b-bot
          ttm01b-top
          ttm02b-bot
          ttm02b-top

    coordsys : string {'raw', 'earth', 'pax'}
       The coordinate system in which to load the data.

    bin : bool (default: False)
       Whether to load averaged data (only valid for coordsys 'earth'
       and 'pax')

    """
    finf = FILEINFO[tag]
    if bin:
        if coordsys not in ['earth', 'pax']:
            raise Exception("Binned data is only stored in "
                            "the 'earth' and 'pax' coordinate systems.")
        return avm.load(finf.abs_fname + "_" + coordsys + '_b5m.h5')
    else:
        if coordsys in ['pax', 'earth']:
            suffix = '_earth'
        elif coordsys in ['raw']:
            suffix = ''
        else:
            raise Exception('Invalid coordsys specification.')
        dat = avm.load(finf.abs_fname + suffix + '.h5')
        if coordsys == 'pax':
            avm.rotate.earth2principal(dat)
        return dat


def pull(files_info=FILEINFO.values(), test_only=False):
    for finf in files_info:
        ftbx.retrieve(finf)
