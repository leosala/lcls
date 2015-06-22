This directory contains a set of scripts which can be used to analyze and reduce data taken during the LH60 beamtime at XPP.

# Setup

If needed, set up your python environment, e.g. by doing:

```
source ../start_python_env.sh
```

If working with IPython, it could be worthwhile to load a few default modules, loading the `load_defaults.py` script:

```
$ ipython
Python 2.7.9 |Anaconda 2.2.0 (64-bit)| (default, Apr 14 2015, 12:54:25) 
In [1]: %load load_defaults.py

In [2]: # %load load_defaults.py
"""
Created on Tue May 26 16:47:06 2015

@author: sala
"""
import h5py
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import sys
import os
XPP_LIB = "../xpp/utilities/"
sys.path.append(os.getcwd() + "/" + XPP_LIB)

import hdf5_utilities as h5u
from images_processor import ImagesProcessor
import xpp_utilities as xpp
import plot_utilities as pu


In [3]: 
```

This would load Numpy, Matplotlib, Pandas and H5Py libraries. For more details about the utilities contained in the `xpp` directory, please check https://github.com/leosala/lcls/tree/master/xpp.

# Usage examples

**INFO:** in general, in these scripts there are some *hard-coded* quantities, such us the directory where data resides, or ROIs, or thresholds, etc. Please have a look at the source code for this.

## Checking a run

If you want to check basic quantities of a run, such as:
* I0
* Average of CsPad images
* ADU plots

then you can use the `check_run.py` script, by simply stating:
```
python check_run.py <run_number>
```
where `<run_number>` is the integer identifying the run number. 

## Creating a file with dark corrections / bad pixels maps

`create_dark_badpixelmap.py` will either create an HDF5 file with *dark background* corrections (detector response in absence of x-rays), or a map with bad pixels (usually, randomly hot ones). The switch between the two behaviours is encoded in the script, please edit it before running!

Running the script in "dark mode" will create a file with:
* the average maps for the CsPad detectors (aka the corrections)
* the standard deviation maps
* the ADU histograms

Instead, when run into "bad pixel" mode it will create boolean masks, identifying the pixels that should be either removed or corrected during analysis. The metric to identify those pixels depends: in this script, pixels with an average value greater than some threshold for a specific run (x-rays, but no sample) are masked.

The script can be run with:

```
python create_dark_badpixelmap.py <run_number>
```

## Get the response of the FEE Spectrometer

In order to do this, you need a scan of electron beam energies (in this case, runs 19-26, already hardcoded in the script).

The `get_fee_spectrometer_response.py` script will plot normalized spectral distributions, and fit the envelope wiht a polynomial (which is printed in the output).

Spectra are summed up, and then normalized to the sum of the `Ch2` I0 monitor: the envelope is retrieved performing a fit for the maximum of each spectra.

