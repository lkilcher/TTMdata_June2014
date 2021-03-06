"""
This data is from measurements at Admiralty Head, in Admiralty Inlet
(Puget Sound) in June of 2014. The measurements were made using
Inertial Motion Unit (IMU) equipped ADVs mounted on Tidal Turbulence
Mooring's (TTMs). The TTM positions the ADV head above the seafloor
to make mid-depth turbulence measurements. The inertial measurements
from the IMU allows for removal of mooring motion in post processing.

The mooring motion has been removed from the stream-wise and vertical
velocity signals (u, w). The lateral (v) velocity has some
'persistent motion contamination' due to mooring sway.

Each ttm was deployed with two ADVs. The 'top' ADV head was positioned
0.5m above the 'bottom' ADV head. The TTMs were placed in 58m of
water. The position of the TTMs were:

ttm01  : (48.1525, -122.6867)
ttm01b : (48.15256666, -122.68678333)
ttm02b : (48.152783333, -122.686316666)

Deployments TTM01b and TTM02b occurred simultaneously.

Files
-----

This data contains the following files:

**<basefile>_<date>_Average5min.csv**

This file contains 5minute averages of the velocity, and the
turbulence intensity.

**<basename>_<date>.vec**

This is the full binary Nortek-format data file. For information on
this data format see Nortek's 'System Integration Manual' available
at: http://www.nortek-as.com/en/support/application-development

**<basename>_<date>_mc.h5**

This file contains a 'lightly processed' version of the raw data in
hdf5 format. This file can be read directly by the DOLfYN library's
'load' function, or using other hdf5 I/O tools such as HDFView. Time
is available in MatPlotLib time (mpltime) format.

**<basename>_<date>_mc.mat**

This file contains the key variables (u, urot, uacc, orientmat, Accel,
AngRt) from the .h5 file, in Matlab format. Time is available in
Matlab 'datenum' format.

**process_data.py**

A script that utilizes the DOLfYN library to read the binary .vec
file, and produce the other files in this dataset.


Units
-----

- Velocity data (_u, urot, uacc) is in m/s.
- Acceleration (Accel) data is in m/s^2.
- Angular rate (AngRt) data is in rad/s.
- The components of all vectors are in 'ENU' orientation. That is, the
  first index is True East, the second is True North, and the third is
  Up (vertical).
- All other quantities are in the units defined in the Nortek Manual.

Motion correction and rotation into the ENU earth reference frame was
performed using the Python-based open source DOLfYN library
(http://lkilcher.github.io/dolfyn/). Details on motion correction can
be found there.

Additional details on TTM measurements at this site can be found in
Thomson et al. 2013, 'Tidal Turbulence measurements from a compliant
mooring' Marine Energy Technology Symposium paper, available here:
http://faculty.washington.edu/jmt3rd/Publications/Thomson_etal_GMREC-METS_2013_turbulencemooring.pdf

Example Usage
=============

Data can be loaded from this package as::

  import June2014 as j14

  dat = j14.load('TTM01-top', coordsys='earth')

"""
from main import *
