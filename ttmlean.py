# from scipy.io import loadmat
import scipy.signal as sig
import matplotlib.pyplot as plt
import numpy as np
import dolfyn.adv.api as avm
plt.ion()


def within(dat, minval, maxval):
    return (minval < dat) & (dat < maxval)

flag = {}
#flag['show_raw_pos'] = True
flag['bt_filt_spec'] = True

filt_freqs = {'5s': 1. / 5,
              '10s': 1. / 10,
              '30s': 1. / 30}

# 4800 points is 5min at 16hz
binner = avm.TurbBinner(4800, 16)

# 20 degrees between ADV body and mooring, rotated around the y-axis.
ang = (18.0 + 180) * np.pi / 180
moor2head_rotmat = np.array([[np.cos(ang), 0, np.sin(ang)],
                             [0, 1, 0],
                             [-np.sin(ang), 0, np.cos(ang)]])
# The distance from the anchor to the ADV IMU, in meters
l_adv_mooring = 10.0

if 'dat' not in vars():
    # Load the 'raw' (unprocessed) data that corresponds to the file above.
    dat = avm.load('ADV/ttm02b_ADVtop_NREL03_June2014' + '.h5')
    # The orientation matrix (orientmat) of the ADV rotates vectors
    # from the earth frame to the instrument frame.

    moor2earth_rotmat = np.einsum('jik,jl,lm->imk',
                                  dat.orientmat,  # body2earth_rotmat (with transpose in index: ji)
                                  dat.props['body2head_rotmat'].T,  # head2body_rotmat
                                  moor2head_rotmat)

    # Multiply the mooring's z-vector, in the earth-frame, by the
    # length of the mooring to get the position of the mooring as a fn
    # of time.
    dat.add_data('posmoor', moor2earth_rotmat[:, 2] * l_adv_mooring, 'orient')

    dat_filt = {}
    bindat_filt = {}
    for filt_tag, filt_freq in filt_freqs.iteritems():
        datmc = dat.copy()
        avm.motion.correct_motion(datmc, accel_filtfreq=filt_freq)

        velmoor = np.pad(np.diff(dat.posmoor) * dat.fs, ([0, 0], [0, 1]), 'edge')

        # The posmoor data is in the earth frame, and datmc is now also.
        filt = sig.butter(2, filt_freq / (dat.fs / 2))
        datmc.add_data('velmoor', sig.filtfilt(filt[0], filt[1],
                                               velmoor),
                       'orient')
        datmc.vel += datmc.velmoor  # Add the bt to the vel
        datmc.rotate_vars.update({'velmoor', })
        dat_filt[filt_tag] = datmc

        datnow = datmc.copy()
        avm.rotate.earth2principal(datnow)

        datbd = binner(datnow)
        datbd.Spec_velraw = binner.psd(datnow.velraw)
        datbd.Spec_velacc = binner.psd(datnow.velacc)
        datbd.Spec_velrot = binner.psd(datnow.velrot)
        datbd.Spec_velmoor = binner.psd(datnow.velmoor)
        datbd.Spec_velmot = binner.psd(datnow.velacc +
                                     datnow.velrot +
                                     datnow.velmoor)
        bindat_filt[filt_tag] = datbd


if flag.get('show_raw_pos', False):

    dtmp = dat.subset(slice(100000))

    fig = plt.figure(10)
    fig.clf()
    fig, axs = plt.subplots(2, 1, num=fig.number)

    ax = axs[0]
    ax.plot(dtmp.posmoor[0], linewidth=2, color='b')
    ax.plot(dtmp.posmoor[1], linewidth=2, color='g')

    ax = axs[1]
    ax.plot(dtmp.posmoor[2], color='k')
    fig.savefig('fig/MooringPosition01.png')


if flag.get('bt_filt_spec', False):

    line = {'x': np.array([1e-5, 100])}
    line['y'] = 2e-4 * line['x'] ** (-5. / 3)

    velrange = [2.0, 2.5]
    #velrange = [0.5, 1.0]
    for ifilt, (filt_tag, filt_freq) in enumerate(filt_freqs.iteritems()):
        datbd = bindat_filt[filt_tag]

        fig = plt.figure(330 + ifilt, figsize=[5.5, 9.5])
        fig.clf()
        fig, axs = plt.subplots(3, 1, num=fig.number,
                                gridspec_kw=dict(right=0.75,
                                                 top=0.97,
                                                 bottom=0.05,
                                                 hspace=0.08),
                                sharex=True, sharey=True)

        inds = within(np.abs(datbd.u), *velrange)
        noise = [1e-5, 1e-5, 2e-6]
        
        for iax, ax in enumerate(axs):
            ax.loglog(datbd.freq,
                      datbd.Spec[iax][inds].mean(0) - noise[iax],
                      'g', label='$u$', linewidth=2, zorder=10)
            ax.loglog(datbd.freq,
                      datbd.Spec_velraw[iax][inds].mean(0) - noise[iax],
                      'y', label='$u_{raw}$')
            ax.loglog(datbd.freq,
                      datbd.Spec_velmot[iax][inds].mean(0),
                      'k', label='$u_{mot}$', zorder=8, linewidth=1.5)
            ax.loglog(datbd.freq,
                      datbd.Spec_velrot[iax][inds].mean(0),
                      'm', label='$u_{rot}$')
            ax.loglog(datbd.freq,
                      datbd.Spec_velacc[iax][inds].mean(0),
                      'b', label='$u_{acc}$')
            ax.loglog(datbd.freq,
                      datbd.Spec_velmoor[iax][inds].mean(0),
                      'r', label='$u_{moor}$')
            ax.plot(line['x'], line['y'], 'k--')
            ax.axvline(filt_freq, linestyle=':', color='k')

        ax.set_xlim([1e-3, 2])
        ax.set_ylim([1e-5, 1])
        axs[0].set_title('{} filter'.format(filt_tag))
        axs[0].legend(bbox_to_anchor=[1.02, 1], loc='upper left')

        # fig.savefig('fig/TTM_velmoor_spec_filt{}.pdf'.format(filt_tag))
