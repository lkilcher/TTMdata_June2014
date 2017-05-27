# from scipy.io import loadmat
import scipy.signal as sig
import matplotlib.pyplot as plt
import numpy as np
import dolfyn.adv.api as avm
from base import datdir


def within(dat, minval, maxval):
    return (minval < dat) & (dat < maxval)

# 20 degrees between ADV body and mooring, rotated around the y-axis.
ang = (18.0 + 180) * np.pi / 180
moor2head_rotmat = np.array([[np.cos(ang), 0, np.sin(ang)],
                             [0, 1, 0],
                             [-np.sin(ang), 0, np.cos(ang)]])
# The distance from the anchor to the ADV IMU, in meters
l_adv_mooring = 10.0

pii = 2 * np.pi


def correct_motion(dat, filt_freq):

    datmc = dat.copy()
    avm.motion.correct_motion(datmc, accel_filtfreq=filt_freq)

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

    datmc.add_data('velmoor_nofilt',
                   np.pad(np.diff(datmc.posmoor) * datmc.fs,
                          ([0, 0], [0, 1]),
                          'edge'),
                   'orient')
    filt = sig.butter(2, filt_freq / (datmc.fs / 2))
    datmc.add_data('velmoor',
                   sig.filtfilt(filt[0], filt[1],
                                datmc.velmoor_nofilt),
                   'orient')
    datmc.vel += datmc.velmoor  # Add velmoor to the vel

    datmc.props['rotate_vars'].update({'posmoor', 'velmoor_nofilt', 'velmoor'})
    return datmc


def bin(datnow):

    # 4800 points is 5min at 16hz
    binner = avm.TurbBinner(5 * 60 * datnow.fs, datnow.fs)
    datbd = binner(datnow)
    datbd.add_data('Spec_velraw', binner.psd(datnow.velraw), 'orient')
    datbd.add_data('Spec_velacc', binner.psd(datnow.velacc), 'orient')
    datbd.add_data('Spec_velrot', binner.psd(datnow.velrot), 'orient')
    datbd.add_data('Spec_velmoor', binner.psd(datnow.velmoor), 'orient')
    datbd.add_data('Spec_velmoor_nofilt',
                   binner.psd(datnow.velmoor_nofilt),
                   'orient')
    datbd.add_data('Spec_velmot',
                   binner.psd(datnow.velacc +
                              datnow.velrot +
                              datnow.velmoor),
                   'orient')
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

    fig = plt.figure(fignum, figsize=[1 + 2 * len(vranges), 6.5])
    fig.clf()
    fig, AXS = plt.subplots(3, len(vranges), num=fig.number,
                            gridspec_kw=dict(right=0.82,
                                             left=0.1,
                                             top=0.9,
                                             bottom=0.1,
                                             hspace=0.1,
                                             wspace=0.1),
                            sharex=True, sharey=True)

    for icol, vrng in enumerate(vranges):
        axs = AXS[:, icol]
        inds = within(np.abs(datbd.u), *vrng)
        noise = [1e-5, 1e-5, 2e-6]

        for iax, ax in enumerate(axs):
            ax.loglog(datbd.freq,
                      (datbd.Spec[iax][inds].mean(0) - noise[iax]) * pii,
                      'g', label='$u$', linewidth=2, zorder=10)
            ax.loglog(datbd.freq,
                      (datbd.Spec_velraw[iax][inds].mean(0) - noise[iax]) * pii,
                      'y', label='$u_{raw}$')
            ax.loglog(datbd.freq,
                      datbd.Spec_velmot[iax][inds].mean(0) * pii,
                      'k', label='$u_{mot}$', zorder=8, linewidth=1.5)
            ax.loglog(datbd.freq,
                      datbd.Spec_velrot[iax][inds].mean(0) * pii,
                      'm', label='$u_{rot}$')
            ax.loglog(datbd.freq,
                      datbd.Spec_velacc[iax][inds].mean(0) * pii,
                      'b', label='$u_{acc}$')
            if 'Spec_velmoor' in datbd:
                ax.loglog(datbd.freq,
                          datbd.Spec_velmoor[iax][inds].mean(0) * pii,
                          'r', label='$u_{moor}$')
            ax.plot(line['x'], line['y'], 'k--')
            try:
                ax.axvline(datbd.props['motion accel_filtfreq Hz'],
                           linestyle=':', color='k')
            except:
                ax.axvline(datbd.props['motion accel filfreq Hz'],
                           linestyle=':', color='k')
        axs[0].set_title('${}<|u|<{}$'.format(*vrng))
    ax.set_xlim([1e-3, 2])
    ax.set_ylim([1e-4, 1])
    AXS[0, -1].legend(bbox_to_anchor=[1.02, 1], loc='upper left')

    for ax in AXS[-1, :]:
        ax.set_xlabel('$f\ \mathrm{[Hz]}$')
    for ax in AXS[:, 0]:
        ax.set_ylabel('$\mathrm{[m^2s^{-2}/Hz]}$')

    return fig, AXS


filt_freqs = {'5s': 0.2,
              '10s': 0.1,
              '30s': 0.03}


def process(fname='ttm02b_ADVtop_NREL03_June2014'):

    dat = avm.load(datdir + fname + '.h5')

    for filt_tag, filt_freq in filt_freqs.iteritems():

        datmc = correct_motion(dat, filt_freq)
        datpx = datmc.copy()
        avm.rotate.earth2principal(datpx)
        datbd = bin(datpx)
        datbd.save(datdir + fname + '_velmoor-f{}_b5m.h5'.format(filt_tag))


def make_pos_time_fig(fname='ttm02b_ADVtop_NREL03_June2014'):

    dat = correct_motion(avm.load(datdir + fname + '.h5'), 0.1)
    fig, axs = plot_raw_pos(dat)
    axs[0].set_ylim([-6, 6])
    fig.savefig(datdir + '../fig/' + fname + '_PosMooring.pdf')


def make_vel_spec_figs(fname='ttm02b_ADVtop_NREL03_June2014'):

    for idx, (filt_tag, filt_freq) in enumerate(
            filt_freqs.iteritems()):
        datbd = avm.load(datdir + fname +
                         '_velmoor-f{}_b5m.h5'.format(filt_tag))
        fig, AXS = plot_bt_filt_spec(300 + idx, datbd)
        fig.suptitle('{} filter'.format(filt_tag))
        fig.savefig(datdir + '../fig/' + fname + '_velmoor_spec_filt{}.pdf'
                    .format(filt_tag))


if __name__ == '__main__':

    process()
    make_vel_spec_figs()
    make_pos_time_fig()
