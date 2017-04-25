import dolfyn.adv.api as avm
from dolfyn.tools import within
from dolfyn.data.time import num2date
import numpy as np
from os.path import isfile

# The file names:
fnames = {
    'ttm01-bot': 'ttm01_ADVbot_NREL01_June2014',
    'ttm01-top': 'ttm01_ADVtop_NREL02_June2014',
    'ttm01b-bot': 'ttm01b_ADVbot_NREL01_June2014',
    'ttm01b-top': 'ttm01b_ADVtop_NREL02_June2014',
    'ttm02b-bot': 'ttm02b_ADVbot_F01_June2014',
    'ttm02b-top': 'ttm02b_ADVtop_NREL03_June2014',
}

# Some variables for calculating dissipation rate (\epsilon)
eps_freqs = np.array([[.3, 1],
                      [.3, 1],
                      [.3, 3], ])
spec_noise = [1.5e-4,
              1.5e-4,
              1.5e-5, ]
pii = 2 * np.pi

mc = avm.motion.CorrectMotion()


def run(tags=fnames.keys(), read_raw=None, save_csv=False):
    """
    Process the ADV data.

    Parameters
    ----------
    tags : iterable
         A list of data tags that you want to process (default: all of
         them).
    read_raw : {True, None, False}
         Whether to read the raw ``.vec`` file, or load the ``.h5``
         file. Default: read .h5, if it is available.
    save_csv : bool
         Save the ``_average5min.csv`` files?
    """
    for tag in tags:
        fnm = fnames[tag]
        print("File: {}".format(fnm))
        if read_raw is True or \
           read_raw is None and not isfile(fnm + '.h5'):
            dr = _read_raw(tag, fnm)
        else:
            dr = avm.load(fnm + '.h5')

        drm = correct_motion(dr, fnm)

        print('  Saving matlab file...')
        drm.add_data('datenum', drm.mpltime + 366, 'main')
        drm.save_mat(fnm + '_earth.mat', groups=['orient', 'main'])
        drm.pop_data('datenum')

        bdat = average(drm)

        print("  Saving binned data to hdf5...")
        bdat.save(fnm + '_earth_b5m.h5')

        if save_csv:
            _save_csv(bdat, fnm)

        print("  Rotating to Principal frame...")
        avm.rotate.earth2principal(drm)
        print("  Binning and saving...")
        bdat2 = average(drm)

        bdat2.save(fnm + '_pax_b5m.h5')

        print("Done.")


def _read_raw(fname, tag):
    # Read the raw vector file
    dr = avm.read_nortek(fname + '.vec')

    dr.noise[0] = 0
    dr.noise[1] = 0
    dr.noise[2] = 0

    # Crop the data when the instrument was on the seafloor
    dr = dr.subset(within(dr.mpltime, dr.props['time_range']))

    ##########
    print('  Cleaning the data...')
    dr.u[~within(dr.u, [-2.5, 0.5])] = np.NaN
    avm.clean.fillpoly(dr.u, 3, 12)
    dr.v[~within(dr.v, [-1, 1])] = np.NaN
    avm.clean.fillpoly(dr.v, 3, 12)
    dr.v[~within(dr.w, [-1, 1])] = np.NaN
    avm.clean.fillpoly(dr.w, 3, 12)
    avm.clean.GN2002(dr.u)
    avm.clean.GN2002(dr.v)
    avm.clean.GN2002(dr.w)
    for nm, d in dr.iter():
        if isinstance(d, np.ndarray) and \
           d.dtype == np.float64 and nm not in ['mpltime']:
            dr[nm] = d.astype(np.float32)
    if dr.has_imu():
        (dr.pitch,
         dr.roll,
         dr.heading) = avm.rotate.orient2euler(dr.orientmat)
    print('  Saving...')
    dr.save(fname + '.h5',
            units={
                'vel': 'm/s', 'velrot': 'm/s',
                'velacc': 'm/s', 'AngRt': 'rad/s',
                'Accel': 'm/s^2', 'AccelStable': 'm/s^2',
                'pitch': 'deg', 'roll': 'deg', 'heading': 'deg true',
                'mpltime': 'MatPlotLib Time format',
                'time': 'ISO8601 time strings.', },
            description={
                'vel': 'Velocity array 0:True East, 1: True North, 2: Up',
                'velrot': 'The rotation-rate velocity.',
                'velacc': 'The tranlational (acceleration) velocity.',
                'AccelStable': 'The low-frequency acceleration '
                'that is ignored in calculating velacc.',
                'pitch': 'The pitch of the ADV body',
                'roll': 'The roll of the ADV body',
                'heading': 'The heading (True) of the ADV body',
                'orientmat': "The orientation matrix of the"
                " ADV body in the Earth's reference frame", })
    return dr


def _save_csv(bdat, fnm):

        ti = bdat.sigma_Uh / bdat.U_mag
        ti[bdat.U_mag < 0.7] = np.NaN

        print("  Saving average csv file...")
        np.savetxt(fnm + '_Average5min.csv',
                   np.vstack((num2date(bdat.mpltime), bdat.u,
                              bdat.v, bdat.w, ti)).T,
                   fmt=['%s'] + ['%0.3f'] * 4,
                   header='Date+Time (US/Pacific), u (true east m/s), '
                          'v (true north m/s), w (up m/s), '
                          'Turbulence Intensity',
                   delimiter=', ')


def correct_motion(dr, fnm):

    print('  Motion correcting...')
    drm = dr.copy()
    mc(drm)
    (drm.pitch[:],
     drm.roll[:],
     drm.heading[:]) = avm.rotate.orient2euler(drm.orientmat)
    print('  Saving...')
    drm.save(fnm + '_earth.h5',
             units={
                 'vel': 'm/s', 'velrot': 'm/s',
                 'velacc': 'm/s', 'AngRt': 'rad/s',
                 'Accel': 'm/s^2', 'AccelStable': 'm/s^2',
                 'pitch': 'deg', 'roll': 'deg', 'heading': 'deg true',
                 'mpltime': 'MatPlotLib Time format',
                 'time': 'ISO8601 time strings.', },
             description={
                 'vel': 'Velocity array 0:True East, 1: True North, 2: Up',
                 'velrot': 'The rotation-rate velocity.',
                 'velacc': 'The tranlational (acceleration) velocity.',
                 'AccelStable': 'The low-frequency acceleration that'
                 ' is ignored in calculating velacc.',
                 'pitch': 'The pitch of the ADV body',
                 'roll': 'The roll of the ADV body',
                 'heading': 'The heading (True) of the ADV body',
                 'orientmat': "The orientation matrix of the ADV "
                 "body in the Earth's reference frame", })
    return drm


def average(dat):
    print("  Averaging...")
    bnr = avm.TurbBinner(n_bin=5 * 60 * dat.fs, fs=dat.fs)

    # This is just a shortcut
    velmot = dat.velacc + dat.velrot

    bdat = bnr(dat)

    # Calculate spectra ####
    bdat.add_data('Spec_velrot',
                  bnr.calc_vel_psd(dat.velrot, ),
                  'spec')
    bdat.add_data('Spec_velacc',
                  bnr.calc_vel_psd(dat.velacc, ),
                  'spec')
    bdat.add_data('Spec_velmot',
                  bnr.calc_vel_psd(velmot, ),
                  'spec')
    bdat.add_data('Spec_velraw',
                  bnr.calc_vel_psd(dat.velraw, ),
                  'spec')

    # Calculate cross-spectra ('point cross-spectra') ####
    bdat.props['Cspec_comp'] = ['uv', 'uw', 'vw']
    bdat.add_data('Cspec_vel',
                  bnr.calc_vel_cpsd(dat.vel).astype(np.complex64),
                  'spec')
    bdat.add_data('Cspec_velmot',
                  bnr.calc_vel_cpsd(velmot).astype(np.complex64),
                  'spec')
    bdat.add_data('Cspec_velraw',
                  bnr.calc_vel_cpsd(dat.velraw).astype(np.complex64),
                  'spec')

    # Calculate triple products ####
    # setup
    bdat.props['tripprod_comp'] = [['uuu', 'uuv', 'uuw', ],
                                   ['vvu', 'vvv', 'vvw', ],
                                   ['wwu', 'wwv', 'www', ]]
    bdat.add_data('tripprod',
                  np.empty((3, 3, len(bdat.u)),
                           dtype=np.float32),
                  'turb')
    # Calculate
    turb = bnr.demean(dat.vel)
    for i0 in range(3):
        for i1 in range(3):
            bdat.tripprod[i0, i1] = (turb[i0] ** 2 * turb[i1]).mean(-1)

    # Calculate the dissipation rate ####
    epstmp = np.zeros_like(bdat.u)
    Ntmp = 0
    for idx, frq_rng in enumerate(eps_freqs):
        if frq_rng is None:
            continue
        om_rng = frq_rng * pii
        N = ((om_rng[0] < bdat.omega) & (bdat.omega < om_rng[1])).sum()
        sptmp = bdat.Spec[idx] - spec_noise[idx] / pii
        sptmp[sptmp < 0] = 0
        tmp = bnr.calc_epsilon_LT83(sptmp,
                                    bdat.omega,
                                    np.abs(bdat.U),
                                    om_rng)
        epstmp += tmp * N
        Ntmp += N
    epstmp /= Ntmp
    # epstmp[np.abs(dat.U) < 0.2] = np.NaN
    bdat.add_data('epsilon', epstmp, 'main')
    return bdat

if __name__ == '__main__':

    run()
