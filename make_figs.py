from __future__ import print_function
# This script works with dolfyn version 0.3.6
import plot_tools as pmod
import matplotlib.pyplot as plt
import numpy as np
reload(pmod)
import matplotlib.dates as dt
from calendar import month_name as month
import base as j14

flag = {}
flag['multi_spec01'] = True
#flag['time01'] = True
#flag['time_comb'] = True

if 'data' not in vars():
    data = {}
print('')
for ftag, fn in j14.files.iteritems():
    print('Creating figures {}...'.format(ftag))
    if ftag not in data:
        print('  Loading data...')
        data[ftag] = j14.load(ftag, bin=True)
        data[ftag].source_file = fn

    dat = data[ftag]

    if flag.get('multi_spec01', False):
        print('  Creating Spec01...', end=' ')
        fig, axs = pmod.multi_spec_plot(
            dat, 1100,
            uranges=np.arange(0, 2.6, 0.5),
            axsize=2,
            noise_level=dict(Spec=[2e-4, 2e-4, 2e-5],
                             Spec_velraw=[2e-4, 2e-4, 2e-5],))
        ax = axs[0, 0]
        ax.set_xlim([1e-3, 10])
        ax.set_ylim([1e-5, 1])
        fig.text(0.5, 0.02, ftag, ha='center', va='bottom')
        figfile = 'fig/{}_Spec01.pdf'.format(ftag)
        print('saving ...', end='')
        fig.savefig(figfile)
        print('Done.')

    if flag.get('time01', False):
        print('  Creating Time01...', end=' ')
        fig, axs = pmod.vel_time(dat, 1200, )
        axs[0].set_ylim([-2.5, 2.5])
        axs[1].set_ylim([-1.0, 1.0])
        axs[2].yaxis.set_ticks(np.arange(-1, 1, 0.1))
        axs[2].set_ylim([-0.2, 0.2])
        axs[2].xaxis.set_major_locator(dt.HourLocator(range(0, 24, 6)))
        axs[2].xaxis.set_major_formatter(dt.DateFormatter('%d.%H'))
        axs[2].xaxis.set_minor_locator(dt.HourLocator())
        axs[2].set_xlabel('Local Time [Day.Hour {}, {}]'
                          .format(month[dat.mpltime.month[0] + 1], dat.mpltime.year[0]))
        figfile = 'fig/{}_VelTime01.pdf'.format(ftag)
        print('saving...', end=' ')
        fig.savefig(figfile)
        print('Done.')

    if flag.get('time_comb', False):
        print('  Creating VelComb01...', end=' ')
        fig, ax = pmod.vel_time_comb(dat, 1300, )
        ax.xaxis.set_major_locator(dt.HourLocator(range(0, 24, 6)))
        ax.xaxis.set_major_formatter(dt.DateFormatter('%d.%H'))
        ax.xaxis.set_minor_locator(dt.HourLocator())
        ax.set_xlabel('Local Time [Day.Hour {}, {}]'
                      .format(month[dat.mpltime.month[0] + 1], dat.mpltime.year[0]))
        figfile = 'fig/{}_VelComb01.pdf'.format(ftag)
        print('saving...', end=' ')
        fig.savefig(figfile)
        print('Done.')

