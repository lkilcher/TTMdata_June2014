# from scipy.io import loadmat
import scipy.signal as sig
import matplotlib.pyplot as plt
import numpy as np
import dolfyn.adv.api as avm
plt.ion()


def within(dat, minval, maxval):
    return (minval < dat) & (dat < maxval)

# 4800 points is 5min at 16hz
binner = avm.TurbBinner(4800, 16)

# 20 degrees between ADV body and mooring, rotated around the y-axis.
ang = (18.0 + 180) * np.pi / 180
moor2head_rotmat = np.array([[np.cos(ang), 0, np.sin(ang)],
                             [0, 1, 0],
                             [-np.sin(ang), 0, np.cos(ang)]])
# The distance from the anchor to the ADV IMU, in meters
l_adv_mooring = 10.0


def correct_motion(dat, filt_freq):

    datmc = dat.copy()
    moor2earth_rotmat = np.einsum(
        'jik,jl,lm->imk',
        datmc.orientmat,  # body2earth_rotmat (with transpose in index: ji)
        datmc.props['body2head_rotmat'].T,  # head2body_rotmat
        moor2head_rotmat)

    # Multiply the mooring's z-vector, in the earth-frame, by the
    # length of the mooring to get the position of the mooring as a fn
    # of time.
    datmc.add_data('posmoor',
                   moor2earth_rotmat[:, 2] * l_adv_mooring,
                   'orient')

    avm.motion.correct_motion(datmc, accel_filtfreq=filt_freq)
    filt = sig.butter(2, filt_freq / (datmc.fs / 2))

    datmc.add_data('velmoor_nofilt',
                   np.pad(np.diff(datmc.posmoor) * datmc.fs,
                          ([0, 0], [0, 1]),
                          'edge'),
                   'orient')
    datmc.add_data('velmoor',
                   sig.filtfilt(filt[0], filt[1],
                                datmc.velmoor_nofilt),
                   'orient')
    datmc.vel += datmc.velmoor  # Add velmoor to the vel

    datmc.rotate_vars.update({'posmoor', 'velmoor_nofilt', 'velmoor'})
    return datmc


def bin(datnow):

    datbd = binner(datnow)
    datbd.Spec_velraw = binner.psd(datnow.velraw)
    datbd.Spec_velacc = binner.psd(datnow.velacc)
    datbd.Spec_velrot = binner.psd(datnow.velrot)
    datbd.Spec_velmoor = binner.psd(datnow.velmoor)
    datbd.Spec_velmoor_nofilt = binner.psd(datnow.velmoor_nofilt)
    datbd.Spec_velmot = binner.psd(datnow.velacc +
                                   datnow.velrot +
                                   datnow.velmoor)
    return datbd


def plot_raw_pos(dat):

    fig = plt.figure(10)
    fig.clf()
    fig, axs = plt.subplots(2, 1, num=fig.number)

    ax = axs[0]
    ax.plot(dat.posmoor[0], linewidth=2, color='b')
    ax.plot(dat.posmoor[1], linewidth=2, color='g')

    ax = axs[1]
    ax.plot(dat.posmoor[2], color='k')
    return fig, axs


def plot_bt_filt_spec(fignum, datbd):

    line = {'x': np.array([1e-5, 100])}
    line['y'] = 2e-4 * line['x'] ** (-5. / 3)

    vranges = [(0.0, 0.5), (1.0, 1.5), (2.0, 2.5)]

    fig = plt.figure(fignum, figsize=[1.5 + 3 * len(vranges), 9.5])
    fig.clf()
    fig, AXS = plt.subplots(3, len(vranges), num=fig.number,
                            gridspec_kw=dict(right=0.86,
                                             left=0.08,
                                             top=0.93,
                                             bottom=0.08,
                                             hspace=0.08,
                                             wspace=0.08),
                            sharex=True, sharey=True)

    for icol, vrng in enumerate(vranges):
        axs = AXS[:, icol]
        inds = within(np.abs(datbd.u), *vrng)
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
            ax.axvline(datbd.props['motion accel_filtfreq Hz'],
                       linestyle=':', color='k')
        axs[0].set_title('${}<|u|<{}$'.format(*vrng))
    ax.set_xlim([1e-3, 2])
    ax.set_ylim([1e-5, 1])
    AXS[0, -1].legend(bbox_to_anchor=[1.02, 1], loc='upper left')

    for ax in AXS[-1, :]:
        ax.set_xlabel('$f\ \mathrm{[Hz]}$')
    for ax in AXS[:, 0]:
        ax.set_ylabel('$\mathrm{[m^2s^{-2}/Hz]}$')

    return fig, AXS


if __name__ == '__main__':

    filt_freqs = {'5s': 0.2,
                  '10s': 0.1,
                  '30s': 0.03}

    fname = 'ADV/ttm02b_ADVtop_NREL03_June2014'
    dat = avm.load(fname + '.h5')

    for idx, (filt_tag, filt_freq) in enumerate(
            filt_freqs.iteritems()):

        datmc = correct_motion(dat, filt_freq)
        datpx = datmc.copy()
        avm.rotate.earth2principal(datpx)
        datbd = bin(datpx)
        datbd.save(fname + '_velmoor-f{}_b5m.h5'.format(filt_tag))

        fig, AXS = plot_bt_filt_spec(300 + idx, datbd)
        fig.suptitle('{} filter'.format(filt_tag))
        fig.savefig('fig/TTM_velmoor_spec_filt{}.pdf'
                    .format(filt_tag))

    fig, axs = plot_raw_pos(datpx)
    fig.savefig('fig/MooringPosition01.png')
