import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gspec

vels = ['u', 'v', 'w']


def calcFigSize(n, ax=np.array([1, 0]),
                frm=np.array([.5, .5]), norm=False):
    """
    sz,vec = calcFigSize(n,ax,frame) calculates the width (or height)
    of a figure with *n* subplots.  Specify the width (height) of each
    subplot with *ax[0]*, the space between subplots with *ax[1]*, and
    the left/right (bottom/top) spacing with *frame[0]*/*frame[1]*.

    calcFigSize returns *sz*, a scalar, which is the width (or height)
    the figure should be, and *vec*, which is the three element vector
    for input to saxes.

    See also: saxes, axes, calcAxesSize
    """
    if hasattr(n, '__iter__'):
        n = np.sum(n)
    sz = n * ax[0] + (n - 1) * ax[1] + frm[0] + frm[1]
    frm = np.array(frm)
    ax = np.array(ax)
    # This checks that it is not the default.
    if not (isinstance(norm, bool) and not norm):
        frm = frm / sz * norm
        ax = ax / sz * norm
        sz = norm
    v = np.array([frm[0], (sz - frm[1]), ax[1]]) / sz
    return sz, v


def vel_time(data, fignum=None,
             frame=[0.8, 0.2, 0.7, 0.5], axsize=[4, 1.7], gap=0.1, ):
    fsr, vr = calcFigSize(3, [axsize[1], gap], frame[2:4])
    fsc, vc = calcFigSize(1, [axsize[0], gap], frame[:2])

    gs = gspec.GridSpec(3, 1, hspace=gap, wspace=gap,
                        left=vc[0], right=vc[1], bottom=vr[0], top=vr[1], )
    fig = plt.figure(fignum, figsize=[fsc, fsr])

    ax = None
    axout = np.empty((3, ), dtype='O')
    for irow in range(3):
        ax = plt.subplot(gs[irow, 0], sharex=ax, sharey=None)
        ax.plot(data.mpltime, data._u[irow])
        if irow < 2:
            plt.setp(ax.get_xticklabels(), visible=False)
        axout[irow] = ax
        ax.axhline(0, linestyle=':', color='k')
        ax.set_ylabel('$%s\,\mathrm{[m/s]}$' % (vels[irow]))
    return fig, axout


def vel_time_comb(data, fignum=None,
                  frame=[0.8, 1.2, 0.7, 0.5], axsize=[4, 2.4], gap=0.1, ):
    fsr, vr = calcFigSize(1, [axsize[1], gap], frame[2:4])
    fsc, vc = calcFigSize(1, [axsize[0], gap], frame[:2])

    gs = gspec.GridSpec(1, 1, hspace=gap, wspace=gap,
                        left=vc[0], right=vc[1], bottom=vr[0], top=vr[1], )
    fig = plt.figure(fignum, figsize=[fsc, fsr])

    ax = plt.subplot(gs[0, 0], )
    ax.axhline(0, linestyle=':', color='k')
    ax.set_ylabel('m/s')
    for irow in range(3):
        ax.plot(data.mpltime, data._u[irow], label='$%s$' % (vels[irow]))
    ax.legend(loc='upper left', bbox_to_anchor=[1.03, 1])
    return fig, ax


def multi_spec_plot(data,
                    fignum=None,
                    uranges=np.linspace(0, 2, 5),
                    u_abs=True,
                    spec_comps=[0, 1, 2],
                    vars=['Spec_uraw', 'Spec_umot', 'Spec', ],
                    axsize=2,
                    frame=[0.8, 1.3, 0.7, .5],
                    gap=[0.1, 0.1],
                    noise_level={}):
    """

    Parameters
    ----------
    axsize: axes size (inches)
    frame : 4-element tuple (inches)
            [left, right, bottom, top]
    gap: 2-element tuple (inches)
            [horiz, vert]
    """
    ncol = len(uranges) - 1
    nrow = len(spec_comps)
    fsc, vc = calcFigSize(ncol, [axsize, gap[1]], frame[:2])
    fsr, vr = calcFigSize(nrow, [axsize, gap[0]], frame[2:4])
    fig = plt.figure(fignum, figsize=[fsc, fsr])
    fig.clf()
    gs = gspec.GridSpec(nrow, ncol, hspace=gap[0], wspace=gap[1],
                        left=vc[0], right=vc[1], bottom=vr[0], top=vr[1], )
    ax = None
    axout = np.empty((nrow, ncol), dtype='O')
    for icol in range(ncol):
        if u_abs:
            udat = np.abs(data.u)
        else:
            udat = data.u
        inds = ((uranges[icol] < udat) &
                (udat <= uranges[icol + 1]))
        for irow in range(nrow):
            ax = plt.subplot(gs[irow, icol], sharex=ax, sharey=ax)
            for v in vars:
                if v.endswith('_uraw'):
                    label = '$S(u_\mathrm{raw})$'
                    color = 'g'
                elif v.endswith('_umot'):
                    label = '$S(u_\mathrm{mot})$'
                    color = 'r'
                elif v == 'Spec':
                    label = '$S(u)$'
                    color = 'b'
                else:
                    label = '???'
                    color = 'k'
                noise = 0
                if v in noise_level:
                    noise = noise_level[v]
                    if hasattr(noise, '__iter__'):
                        noise = noise[irow]
                if inds.sum() > 0:
                    ax.loglog(data.freq,
                              data[v][irow][inds].mean(0) * 2 * np.pi - noise,
                              label=label, color=color)
            if icol != 0 or irow != (nrow - 1):
                plt.setp(ax.get_yticklabels(), visible=False)
                plt.setp(ax.get_xticklabels(), visible=False)
            axout[irow, icol] = ax
        if u_abs:
            title_format = '${:.1f}<|u|\leq{:.1f}$'
        else:
            title_format = '${:.1f}<u\leq{:.1f}$'
        ax = axout[0, icol]
        ax.set_title(title_format.format(*(uranges[icol:icol + 2])))
        ax.text(0.94, 0.94, 'N={:d}'.format(inds.sum()),
                ha='right', va='top',
                transform=ax.transAxes)
    for irow in range(nrow):
        # axout[irow, 0].text(.92, .92,
        #                     ('$S_{%s%s}$' %
        #                      tuple([vels[spec_comps[irow]]] * 2)),
        #                     transform=axout[irow, 0].transAxes,
        #                     ha='right', va='top')
        axout[irow, -1].text(1.04, 1.0, '${}$'.format(vels[spec_comps[irow]]),
                             ha='left', va='top', transform=axout[irow, -1].transAxes,
                             size='x-large')
    axout[-1, 0].set_ylabel('$\mathrm{[m^2s^{-2}/Hz]}$')
    axout[-1, 0].set_xlabel('$f\,\mathrm{[Hz]}$')
    axout[0, -1].legend(loc='lower left', bbox_to_anchor=[1.04, 0.0],
                        borderaxespad=0.2, labelspacing=0.2, handletextpad=0.2,
                        fontsize='medium', )
    if 'config' in data:
        headnum = data.config.head.serialNum.strip('\x00').lstrip('VEC ')
        fig.text(0.97, 0.02, 'HEAD #: {}'.format(headnum), clip_on=False,
                 ha='right', va='bottom')
        hwnum = data.config.hardware.serialNum.strip('\x00').lstrip('VEC ')
        fig.text(0.96, 0.04, 'HW #: {}'.format(hwnum), clip_on=False,
                 ha='right', va='bottom')
    return fig, axout
