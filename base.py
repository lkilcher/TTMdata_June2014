from os import path
import dolfyn.adv.api as avm

package_root = path.dirname(path.realpath(__file__))

datdir = package_root + '/ADV/'

# The file names:
files = {
    'ttm01-bot': 'ttm01_ADVbot_NREL01_June2014',
    'ttm01-top': 'ttm01_ADVtop_NREL02_June2014',
    'ttm01b-bot': 'ttm01b_ADVbot_NREL01_June2014',
    'ttm01b-top': 'ttm01b_ADVtop_NREL02_June2014',
    'ttm02b-bot': 'ttm02b_ADVbot_F01_June2014',
    'ttm02b-top': 'ttm02b_ADVtop_NREL03_June2014',
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
    if tag in files:
        fname = files[tag]
    elif tag.lower() in files:
        fname = files[tag.lower()]
    if bin:
        if coordsys not in ['earth', 'pax']:
            raise Exception("Binned data is only stored in "
                            "the 'earth' and 'pax' coordinate systems.")
        return avm.load(datdir + fname + "_" + coordsys + '_b5m.h5')
    else:
        if coordsys in ['pax', 'earth']:
            suffix = '_earth'
        elif coordsys in ['raw']:
            suffix = ''
        else:
            raise Exception('Invalid coordsys specification.')
        dat = avm.load(datdir + fname + suffix + '.h5')
        if coordsys == 'pax':
            avm.rotate.earth2principal(dat)
        return dat
