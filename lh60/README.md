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
