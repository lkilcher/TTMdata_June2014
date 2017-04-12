import dolfyn.adv.api as avm
from dolfyn.tools import within
from dolfyn.data.time import date2num, num2date
import datetime
import numpy as np

read_raw = False
#read_raw = True

# The file names:
fnames = {
    'ttm01-bottom': 'ttm01_ADVbottom_NREL01_June2014',
    'ttm01-top': 'ttm01_ADVtop_NREL02_June2014',
    'ttm01b-bottom': 'ttm01b_ADVbottom_NREL01_June2014',
    'ttm01b-top': 'ttm01b_ADVtop_NREL02_June2014',
    'ttm02b-bottom': 'ttm02b_ADVbottom_F01_June2014',
    'ttm02b-top': 'ttm02b_ADVtop_NREL03_June2014',
}

# The time ranges that each TTM was on the seafloor:
# These are calculated by inspection of the signal (e.g. u, v, w, Accel,
# etc...) timeseries.
time_range = {'ttm01': [date2num(datetime.datetime(2014, 6, 16, 21, 12, 0)),
                        date2num(datetime.datetime(2014, 6, 17, 14, 42, 0)), ],
              'ttm01b': [date2num(datetime.datetime(2014, 6, 18, 8, 0, 0)),
                         date2num(datetime.datetime(2014, 6, 19, 5, 12, 0)), ],
              'ttm02b': [date2num(datetime.datetime(2014, 6, 18, 8, 15, 0)),
                         date2num(datetime.datetime(2014, 6, 19, 5, 0, 0)), ],
              }

# Some variables for calculating dissipation rate (\epsilon)
eps_freqs = np.array([[.3, 1],
                      [.3, 1],
                      [.3, 3], ])
spec_noise = [1.5e-4,
              1.5e-4,
              1.5e-5, ]
pii = 2 * np.pi

# The lat/lon values
latlons = {'ttm01b': (48.15256666, -122.68678333),
           'ttm02b': (48.152783333, -122.686316666),
           'ttm01': (48.1525, -122.6867),
           }

# The body-head vectors:
m_in = 0.0254
b2h_vec = {'ttm01-bottom': np.array([-11.5, -0.25, -14.25]) * m_in,
           'ttm01-top': np.array([0.254, -0.064, -0.165])
           }
b2h_vec['ttm01b-top'] = b2h_vec['ttm01-top']
b2h_vec['ttm01b-bottom'] = b2h_vec['ttm01-bottom']
b2h_vec['ttm02b-top'] = np.array([10., -2.5, -5]) * m_in  # in->m
b2h_vec['ttm02b-bottom'] = np.array([-13.25, 2.75, -12.75]) * m_in  # in->m

# The rotation matrices
b2h_rotmat = {}
# They are all the same for the TTMs
(b2h_rotmat['ttm01b-bottom'],
 b2h_rotmat['ttm01-top'],
 b2h_rotmat['ttm01-bottom'],
 b2h_rotmat['ttm02b-top'],
 b2h_rotmat['ttm02b-bottom'],
 b2h_rotmat['ttm01b-top'],) = 6 * [np.array([[0, 0, -1],
                                             [0, -1, 0],
                                             [-1, 0, 0]])]

# binner = avm.TurbBinner(n_bin=10240, fs=32., n_fft=10240, n_fft_coh=2048)

mc = avm.motion.CorrectMotion()

if __name__ == '__main__':

    for tag, fnm in fnames.iteritems():
        print("File: {}".format(fnm))
        source_name = fnm
        if read_raw:
            # Read the raw vector file
            dr = avm.read_nortek(source_name + '.vec')

            # Assign some properties:
            dr.props['body2head_rotmat'] = b2h_rotmat[tag]
            if tag in b2h_vec.keys():
                dr.props['body2head_vec'] = b2h_vec[tag]
            dr.noise[0] = 0
            dr.noise[1] = 0
            dr.noise[2] = 0
            dr.props['latlon'] = latlons[tag.split('-')[0]]

            # Crop the data when the instrument was on the seafloor
            dr = dr.subset(within(dr.mpltime, time_range[tag.split('-')[0]]))

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
            for nm, d in dr.iteritems():
                if isinstance(d, np.ndarray) and d.dtype == np.float64 and nm not in ['mpltime']:
                    dr[nm] = d.astype(np.float32)
            if dr.has_imu():
                dr.pitch, dr.roll, dr.heading = avm.rotate.orient2euler(dr.orientmat)
            print('  Saving...')
            dr.save(fnm + '.h5',
                    units={'vel': 'm/s', 'velrot': 'm/s', 'velacc': 'm/s', 'AngRt': 'rad/s',
                           'Accel': 'm/s^2', 'AccelStable': 'm/s^2',
                           'pitch': 'deg', 'roll': 'deg', 'heading': 'deg true',
                           'mpltime': 'MatPlotLib Time format',
                           'time': 'ISO8601 time strings.', },
                    description={'vel': 'Velocity array 0:True East, 1: True North, 2: Up',
                                 'velrot': 'The rotation-rate velocity.',
                                 'velacc': 'The tranlational (acceleration) velocity.',
                                 'AccelStable': 'The low-frequency acceleration '
                                                'that is ignored in calculating velacc.',
                                 'pitch': 'The pitch of the ADV body',
                                 'roll': 'The roll of the ADV body',
                                 'heading': 'The heading (True) of the ADV body',
                                 'orientmat': "The orientation matrix of the"
                                              " ADV body in the Earth's reference frame", })
        else:
            print('  Loading...')
            dr = avm.load(fnm + '.h5')

        bnr = avm.TurbBinner(n_bin=5 * 60 * dr.fs, fs=dr.fs)
        if dr.has_imu():
            print('  Motion correcting...')
            drm = dr.copy()
            mc(drm)
            drm.pitch[:], drm.roll[:], drm.heading[:] = avm.rotate.orient2euler(drm.orientmat)
            print('  Saving...')
            drm.save(fnm + '_earth.h5',
                     units={'vel': 'm/s', 'velrot': 'm/s', 'velacc': 'm/s', 'AngRt': 'rad/s',
                            'Accel': 'm/s^2', 'AccelStable': 'm/s^2',
                            'pitch': 'deg', 'roll': 'deg', 'heading': 'deg true',
                            'mpltime': 'MatPlotLib Time format',
                            'time': 'ISO8601 time strings.', },
                     description={'vel': 'Velocity array 0:True East, 1: True North, 2: Up',
                                  'velrot': 'The rotation-rate velocity.',
                                  'velacc': 'The tranlational (acceleration) velocity.',
                                  'AccelStable': 'The low-frequency acceleration that'
                                                 ' is ignored in calculating velacc.',
                                  'pitch': 'The pitch of the ADV body',
                                  'roll': 'The roll of the ADV body',
                                  'heading': 'The heading (True) of the ADV body',
                                  'orientmat': "The orientation matrix of the ADV "
                                               "body in the Earth's reference frame", }
            )

        print('  Saving matlab file...')
        drm.add_data('datenum', drm.mpltime + 366, 'main')
        drm.save_mat(fnm + '_earth.mat', groups=['orient', 'main'])
        drm.pop_data('datenum')

        print("  Averaging...")
        bdat = bnr(drm)
        bdat.add_data('Spec_velrot',
                      bnr.calc_vel_psd(drm.velrot, ),
                      'spec')
        bdat.add_data('Spec_velacc',
                      bnr.calc_vel_psd(drm.velacc, ),
                      'spec')
        bdat.add_data('Spec_velmot',
                      bnr.calc_vel_psd(drm.velrot + drm.velacc, ),
                      'spec')
        bdat.add_data('Spec_velraw',
                      bnr.calc_vel_psd(drm.velraw, ),
                      'spec')
        ti = bdat.sigma_Uh / bdat.U_mag
        ti[bdat.U_mag < 0.7] = np.NaN

        print("  Saving average...")
        np.savetxt(fnm + '_Average5min.csv',
                   np.vstack((num2date(bdat.mpltime), bdat.u, bdat.v, bdat.w, ti)).T,
                   fmt=['%s'] + ['%0.3f'] * 4,
                   header='Date+Time (US/Pacific),'
                   ' u (true east m/s), v (true north m/s), w (up m/s), Turbulence Intensity',
                   delimiter=', ')

        print("  Saving binned data to hdf5...")
        bdat.save(fnm + '_earth_b5m.h5')

        print("  Rotating to Principal frame...")
        avm.rotate.earth2principal(drm)
        print("  Binning and saving...")
        bdat2 = bnr(drm)
        velmot = drm.velacc + drm.velrot
        bdat2.add_data('Spec_velrot',
                       bnr.calc_vel_psd(drm.velrot, ),
                       'spec')
        bdat2.add_data('Spec_velacc',
                       bnr.calc_vel_psd(drm.velacc, ),
                       'spec')
        bdat2.add_data('Spec_velmot',
                       bnr.calc_vel_psd(velmot),
                       'spec')
        bdat2.add_data('Spec_velraw',
                       bnr.calc_vel_psd(drm.velraw, ),
                       'spec')
        bdat2.props['Cspec_comp'] = ['uv', 'uw', 'vw']
        bdat2.add_data('Cspec_vel',
                       bnr.calc_vel_cpsd(drm.vel).astype(np.complex64),
                       'spec')
        bdat2.add_data('Cspec_velmot',
                       bnr.calc_vel_cpsd(velmot).astype(np.complex64),
                       'spec')
        bdat2.add_data('Cspec_velraw',
                       bnr.calc_vel_cpsd(drm.velraw).astype(np.complex64),
                       'spec')
        bdat2.props['tripprod_comp'] = [['uuu', 'uuv', 'uuw', ],
                                        ['vvu', 'vvv', 'vvw', ],
                                        ['wwu', 'wwv', 'www', ]]

        bdat2.add_data('tripprod',
                       np.empty((3, 3, len(bdat2.u)),
                                dtype=np.float32),
                       'turb')
        turb = bnr.demean(drm.vel)
        for i0 in range(3):
            for i1 in range(3):
                bdat2.tripprod[i0, i1] = (turb[i0] ** 2 * turb[i1]).mean(-1)

        # Calculate the dissipation rate.
        epstmp = np.zeros_like(bdat2.u)
        Ntmp = 0
        for idx, frq_rng in enumerate(eps_freqs):
            if frq_rng is None:
                continue
            om_rng = frq_rng * pii
            N = ((om_rng[0] < bdat2.omega) & (bdat2.omega < om_rng[1])).sum()
            sptmp = bdat2.Spec[idx] - spec_noise[idx] / pii
            sptmp[sptmp < 0] = 0
            tmp = bnr.calc_epsilon_LT83(sptmp,
                                        bdat2.omega,
                                        np.abs(bdat2.U),
                                        om_rng)
            epstmp += tmp * N
            Ntmp += N
        epstmp /= Ntmp
        # epstmp[np.abs(dat.U) < 0.2] = np.NaN
        bdat2.add_data('epsilon', epstmp, 'main')

        bdat2.save(fnm + '_pax_b5m.h5')

        print("Done.")
