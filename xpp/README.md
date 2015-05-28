# Code for XPP data analysis

## How to set up your environment

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
* `ImagesProcessor`, which contains utilities to analyse and filter images


# Usage example

All the examples assume that you have loaded the modules using `%load load_defaults.py` in an ipython shell

## Getting properly tagged scalar data

In order to properly correlate data, you should take care of pulse-ids (or _tags_). For scalar data, we can use the `get_scalar_data` routine provided by the `xpp` module: this will create a Pandas dataframe, taking care of properly correlate data. 

First, we load the defaults and set up file and datasets names:
```
In [1]: %load load_defaults.py
In [3]: fname = "/reg/d/psdm/xpp/xpph6015/hdf5/xpph6015-r0005.h5"
In [4]: ipm2 = "Lusi::IpmFexV1/XppSb2_Ipm"
In [5]: ipm3 = "Lusi::IpmFexV1/XppSb3_Ipm"
```

Then, we retrieve the data. As can be seen, a limitation is that only scalar (i.e. one value per tag) data can be retrieved in this way:
```
In [7]: df = xpp.get_data(fname, [ipm2, ipm3])
Lusi::IpmFexV1/XppSb2_Ipm
Lusi::IpmFexV1/XppSb3_Ipm
[WARNING] Dataset Lusi::IpmFexV1/XppSb2_Ipm/channel cannot be loaded, as it is not a scalar dataset
[WARNING] Dataset Lusi::IpmFexV1/XppSb3_Ipm/channel cannot be loaded, as it is not a scalar dataset
```

If we do have a look at the first entries, we can see that they are indexed by tags:
```
In [8]: df.head()
Out[8]: 
                  Lusi::IpmFexV1/XppSb2_Ipm.sum  \
tags                                              
1432749224067752                       0.000455   
1432749224067755                       0.000074   
1432749224067758                       0.000684   
1432749224067761                      -0.000689   
1432749224067764                      -0.000079   

[...]

                  Lusi::IpmFexV1/XppSb3_Ipm.sum  \
tags                                              
1432749224067752                      -0.000948   
1432749224067755                      -0.000948   
1432749224067758                      -0.000871   
1432749224067761                      -0.000948   
1432749224067764                       0.000044   
```

Then, using the Pandas plotting utilities, we can easily create e.g. a correlation plot:
```
In [9]: df.plot(kind="scatter", x="Lusi::IpmFexV1/XppSb3_Ipm.sum", y="Lusi::IpmFexV1/XppSb2_Ipm.sum")
Out[9]: <matplotlib.axes._subplots.AxesSubplot at 0x2abc35c1a3d0>

In [10]: plt.show()
```
![example tagged image](https://cloud.githubusercontent.com/assets/4245111/7851213/e4a12d2a-04a0-11e5-8aa4-67c927a17257.png)

# Description of examples

## plot_cspad_tile.py

This is a simple script that plots ADU counts histograms for each of the CsPad140k tiles

## image_analysis.py

This example performs a more complicated set of analyses on the CsPad140. In order to do that, it uses the `ImagesProcessor` class, which provides to properly glue and optimize the analyses. 

## get_rixs_map.py

This example shows how to retrieve data from the FEE spectrometer, filter it out, and then combine it in order to obtain a SASE RIXS map.

