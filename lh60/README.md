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
Type "copyright", "credits" or "license" for more information.

IPython 3.0.0 -- An enhanced Interactive Python.
Anaconda is brought to you by Continuum Analytics.
Please check out: http://continuum.io/thanks and https://binstar.org
?         -> Introduction and overview of IPython's features.
%quickref -> Quick reference.
help      -> Python's own help system.
object?   -> Details about 'object', use 'object??' for extra details.

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
