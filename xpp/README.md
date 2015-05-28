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

A typical environment setup can be obtained by doing:

```
user@hostname:~/Programs/git/lcls$ source start_xpp_env.sh
user@hostname:~/Programs/git/lcls$ ipython
Python 2.7.9 |Anaconda 2.2.0 (64-bit)| (default, Apr 14 2015, 12:54:25) 

In [1]: %load load_defaults.py
In [2]: # %load load_defaults.py
import h5py
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import sys
import os
XPP_LIB = "utilities/"
sys.path.append(os.getcwd() + "/" + XPP_LIB)

import hdf5_utilities as h5u
from images_processor import ImagesProcessor
import xpp_utilities as xpp
import plot_utilities as pu

```


# Usage example

All the examples assume that you have loaded the modules using `%load load_defaults.py` in an ipython shell

## Searching for regular expressions in an HDF5 file

Using the `hdf5_utilities` module (loaded as `h5u`), you can look for regular expressions in an HDF5 file, with also a printout of the corresponding dataset info. For example:

```
In [1]: fname = "/reg/d/psdm/xpp/xpph6015/hdf5/xpph6015-r0005.h5"
In [2]: f = h5py.File(fname, 'r')
In [3]: h5u.search_hdf5(f, "Lusi.*XppSb3_Ipm")
.*Lusi.*XppSb3_Ipm.*
Configure:0000/Run:0000/CalibCycle:0000/Lusi::IpmFexV1/XppSb3_Ipm/data
Configure:0000/Run:0000/CalibCycle:0000/Lusi::IpmFexV1/XppSb3_Ipm/_damage
Configure:0000/Lusi::IpmFexConfigV2/XppSb3_Ipm/config
Configure:0000/Run:0000/CalibCycle:0000/Lusi::IpmFexV1/XppSb3_Ipm/time
Configure:0000/Run:0000/CalibCycle:0000/Lusi::IpmFexV1/XppSb3_Ipm/_mask
Out[38]: 
{u'Configure:0000/Lusi::IpmFexConfigV2/XppSb3_Ipm/config': {'dtype': dtype([('diode', [('base', '<f4', (16,)), ('scale', '<f4', (16,))], (4,)), ('xscale', '<f4'), ('yscale', '<f4')]),
  'shape': ()},
 u'Configure:0000/Run:0000/CalibCycle:0000/Lusi::IpmFexV1/XppSb3_Ipm/_damage': {'dtype': dtype([('bits', '<u4'), ('DroppedContribution', 'u1'), ('OutOfOrder', 'u1'), ('OutOfSynch', 'u1'), ('UserDefined', 'u1'), ('IncompleteContribution', 'u1'), ('userBits', 'u1')]),
  'shape': (1269,)},
 u'Configure:0000/Run:0000/CalibCycle:0000/Lusi::IpmFexV1/XppSb3_Ipm/_mask': {'dtype': dtype('uint8'),
  'shape': (1269,)},
 u'Configure:0000/Run:0000/CalibCycle:0000/Lusi::IpmFexV1/XppSb3_Ipm/data': {'dtype': dtype([('channel', '<f4', (4,)), ('sum', '<f4'), ('xpos', '<f4'), ('ypos', '<f4')]),
  'shape': (1269,)},
 u'Configure:0000/Run:0000/CalibCycle:0000/Lusi::IpmFexV1/XppSb3_Ipm/time': {'dtype': dtype([('seconds', '<u4'), ('nanoseconds', '<u4'), ('ticks', '<u4'), ('fiducials', '<u4'), ('control', '<u4'), ('vector', '<u4')]),
  'shape': (1269,)}}
```

## Printing the structure of an HDF5 file

Similarly, you can also iteratively print out the structure. For example, if you want the tree up to the second level of datasets:

```
In [43]: h5u.print_leaf(f, level=1)
/Configure:0000/Alias::ConfigV1
/Configure:0000/Bld::BldDataEBeamV7
/Configure:0000/Bld::BldDataFEEGasDetEnergyV1
/Configure:0000/Bld::BldDataPhaseCavity
/Configure:0000/Bld::BldDataSpectrometerV1
/Configure:0000/CalibStore
/Configure:0000/Camera::FrameFexConfigV1
/Configure:0000/ControlData::ConfigV3
/Configure:0000/CsPad2x2::ConfigV2
/Configure:0000/Epics::ConfigV1
/Configure:0000/Epics::EpicsPv
/Configure:0000/EvrData::ConfigV7
/Configure:0000/EvrData::IOConfigV2
/Configure:0000/Ipimb::ConfigV2
/Configure:0000/L3T::ConfigV1
/Configure:0000/Lusi::IpmFexConfigV2
/Configure:0000/Lusi::PimImageConfigV1
/Configure:0000/Opal1k::ConfigV1
/Configure:0000/Orca::ConfigV1
/Configure:0000/Partition::ConfigV1
/Configure:0000/Pulnix::TM6740ConfigV2
/Configure:0000/Run:0000
```

## Getting properly tagged scalar data

In order to properly correlate data, you should take care of pulse-ids (or _tags_). For scalar data, we can use the `get_scalar_data` routine provided by the `xpp` module: this will create a Pandas dataframe, taking care of properly correlate data. 

First, we load the defaults and set up file and datasets names:
```
In [1]: %load load_defaults.py
In [2]: fname = "/reg/d/psdm/xpp/xpph6015/hdf5/xpph6015-r0005.h5"
In [3]: ipm2 = "Lusi::IpmFexV1/XppSb2_Ipm"
In [4]: ipm3 = "Lusi::IpmFexV1/XppSb3_Ipm"
```

Then, we retrieve the data. As can be seen, a limitation is that only scalar (i.e. one value per tag) data can be retrieved in this way:
```
In [5]: df = xpp.get_data(fname, [ipm2, ipm3])
Lusi::IpmFexV1/XppSb2_Ipm
Lusi::IpmFexV1/XppSb3_Ipm
[WARNING] Dataset Lusi::IpmFexV1/XppSb2_Ipm/channel cannot be loaded, as it is not a scalar dataset
[WARNING] Dataset Lusi::IpmFexV1/XppSb3_Ipm/channel cannot be loaded, as it is not a scalar dataset
```

If we do have a look at the first entries, we can see that they are indexed by tags:

```
In [6]: df.head()
Out[7]: 
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
In [8]: df.plot(kind="scatter", x="Lusi::IpmFexV1/XppSb3_Ipm.sum", y="Lusi::IpmFexV1/XppSb2_Ipm.sum")
Out[8]: <matplotlib.axes._subplots.AxesSubplot at 0x2abc35c1a3d0>

In [9]: plt.show()
```
![example tagged image](https://cloud.githubusercontent.com/assets/4245111/7851213/e4a12d2a-04a0-11e5-8aa4-67c927a17257.png)

## Get generic tagged data

If you need to retrieve vectors or images, you can just use the `xpp.get_data_with_tags` routine. It will return two arrays: one with the data, one with the tags.

In the following example, we will retrieve the data from a tile of the CsPad140k, and then select only certain tags. As before, we start with the standard loadings:

```
In [1]: %load load_defaults.py
In [2]: fname = "/reg/d/psdm/xpp/xpph6015/hdf5/xpph6015-r0005.h5"
In [3]: cspad0_name = "CsPad2x2::ElementV1/XppGon.0:Cspad2x2.0/data"
```

Then, we get the data and the tags:

```
In [4]: cspad0_data, cspad0_tags = xpp.get_data_with_tags(fname, cspad0_name)
In [5]: print cspad0_data.shape, cspad0_data[0].shape, cspad0_tags.shape
(1269,) (185, 388, 2) (1269,)
```

If we want for example select only certain tags, we can create a boolean mask, and then apply it to the data array:

```
In [6]: mask = (cspad0_tags > 1432749224067764) * (cspad0_tags < 1432749224067800)
In [7]: sel_data = cspad0_data[mask]
In [8]: print sel_data.shape
(11, 185, 388, 2)
```

# Description of examples

## plot_cspad_tile.py

This is a simple script that plots ADU counts histograms for each of the CsPad140k tiles

## image_analysis.py

This example performs a more complicated set of analyses on the CsPad140. In order to do that, it uses the `ImagesProcessor` class, which provides to properly glue and optimize the analyses. 

## get_rixs_map.py

This example shows how to retrieve data from the FEE spectrometer, filter it out, and then combine it in order to obtain a SASE RIXS map.

