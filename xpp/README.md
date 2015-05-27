# Code for XPP data analysis

# How to set up your environment

First, you need to set up the correct python environment, using:

```
source start_xpp_env.sh
```

Then, if you want to work with ipython, you can load the needed modules doing (from the ipython prompt): `%load load_defaults.py`

This will load some standard modules:

* `h5py`
* `numpy` (as np)
* `pandas` (as pd)
* `matplotlib.pyplot` (as plt)

plus some custom designed utilities, as:

* `xpp_utilities` (as xpp), which contains utilities for loading scalar data from XPP hdf5 files, and create the correct pulse tag
* `hdf5_utilities` (as h5u), which contains the `search_hdf5` function (to search for datasets)
* `images_processor` (as ip), which contains utilities to analyse and filter images
