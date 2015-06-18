# -*- coding: utf-8 -*-
"""
Plots emission lines from multiple runs
It applies (if wanted):
+ ADU thresholds
+ dark background corrections
+ bad pixels map
+ ROIs
"""

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import h5py

import sys
XPP_LIB = "../xpp/utilities/"
sys.path.append(XPP_LIB)
import plot_utilities as pu
from images_processor import ImagesProcessor
import xpp_utilities as xpp

## Runs to be analyzed
#runs = [94, 95, 96, 89]
#runs = [77, 81, 84, 79, 83]
#runs = [110, 103, 107, 106, 108]
#runs = [127, 128, ]
#runs = [130, 131, 132, 133, 135, 136, 137, 138, 139, 140]
runs = [152, ]##153, 154, 155, 156, 157]

#DIR = "/reg/d/psdm/XPP/xpph6015/hdf5/"
DIR = "/reg/d/psdm/xpp/xpph6015/ftc/hdf5/"

## ROIs
#roi0 = [[147, 155], [0, 391]]
#roi1 = [[155, 172], [0, 391]]
#roi0 = [[0, 388], [147, 155]]
#roi1 = [[0, 388], [155, 172]]
#roi0 = [[0, 388], [130, 190]]
#roi1 = [[0, 388], [130, 190]]
#roi0 = [[0, 388], [157, 168]]
#roi1 = [[0, 388], [165, 180]]
# from run 127
roi0 = [[0, 388], [150, 160]]
roi1 = [[0, 388], [105, 124]]

# events per run to be analyzed
n_events = 1000

ip = ImagesProcessor()
# the dataset path common to everything:
dset_main = "/Configure:0000/Run:0000/CalibCycle:0000/"

spectra0 = []
spectra1 = []
image_labels = []
images0 = []
images1 = []

# dark corrections
dark_f = h5py.File("data/dark_run0030.h5", "r")
dark0 = dark_f['CsPad0/mean'][:]
dark1 = dark_f['CsPad1/mean'][:]

# masking bad pixels
#bad_f = h5py.File("data/bad_pixels_r129_gt4.h5", "r")
bad_f = h5py.File("bad_pixels_r0126_gt4.0.h5", "r")
bad_pixel_mask0 = bad_f['CsPad0/bad_pixel_mask'][:]
bad_pixel_mask1 = bad_f['CsPad1/bad_pixel_mask'][:]

for run in runs:
    fname = DIR + "xpph6015-r%04d.h5" % run  # DIR + "xpph6015-r0005.h5"
    image_labels.append("Run %d" % run)
    print "Running on %s" %fname
    
    # Starting the Images Processor for CsPad #0
    dset_name = "CsPad2x2::ElementV1/XppGon.0:Cspad2x2.0"
    ip.set_dataset(dset_main + dset_name)
    # addind the analysis
    ip.add_preprocess("correct_bad_pixels", args={"mask": bad_pixel_mask0})
    ip.add_preprocess("subtract_correction", args={'sub_image': dark0})
    ip.add_preprocess("set_thr", args={"thr_low": 25})
    ip.add_preprocess("set_roi", args={'roi': roi0})
    ip.add_analysis('get_mean_std', )
    # special image iterator (CsPad140 needs some special care)
    ip.set_images_iterator('images_iterator_cspad140')
    # run the analysis
    results0 = ip.analyze_images(fname, n=n_events)
    
    dset_name = "CsPad2x2::ElementV1/XppGon.0:Cspad2x2.1"
    ip.set_dataset(dset_main + dset_name)
    ip.add_preprocess("correct_bad_pixels", args={"mask": bad_pixel_mask1})
    ip.add_preprocess("subtract_correction", args={'sub_image': dark1})
    ip.add_preprocess("set_thr", args={"thr_low": 22})
    ip.add_preprocess("set_roi", args={'roi': roi1})
    # addind the analysis
    ip.add_analysis('get_mean_std', )
    # special image iterator (CsPad140 needs some special care)
    ip.set_images_iterator('images_iterator_cspad140')
    # run the analysis
    results1 = ip.analyze_images(fname, n=n_events)
    
    # plot the results
    images_mean0 = results0["get_mean_std"]["images_mean"]
    images_mean1 = results1["get_mean_std"]["images_mean"]
    
    images0.append(images_mean0)    
    images1.append(images_mean1)
    
    # get data from ipmb0
    fname = '/reg/d/psdm/xpp/xpph6015/ftc/hdf5/xpph6015-r%04d.h5' % run
    df_i0 = xpp.get_scalar_data(fname, "Ipimb::DataV2/XppEnds_Ipm0/data", n_events=n_events)
    #df_i0 = xpp.get_scalar_data(fname, "Bld::BldDataFEEGasDetEnergyV1/FEEGasDetEnergy/data", n_events=n_events)
    # using IPM0
    r_norm = 1./ df_i0["Ipimb::DataV2/XppEnds_Ipm0/data.channel2"][0:n_events].sum()
    # Using Gas Monitor
    #r_norm = df_i0["Bld::BldDataFEEGasDetEnergyV1/FEEGasDetEnergy/data.f_11_ENRC"][0:n_events].sum()
    #spectra0.append(images_mean0.sum(axis=1) / float(r_norm))
    #spectra1.append(images_mean1.sum(axis=1) / float(r_norm))
    # Using the max
    spectra0.append(images_mean0.sum(axis=1) / float(images_mean0.sum(axis=1).max()))
    spectra1.append(images_mean1.sum(axis=1) / float(images_mean1.sum(axis=1).max()))
    

# plottting everything+-
plt.figure()
for i, run in enumerate(runs):
    plt.plot(spectra0[i], label=image_labels[i])
plt.legend(loc="best")

plt.figure()
for i, run in enumerate(runs):
    plt.plot(spectra1[i], label=image_labels[i])

plt.legend(loc="best")
plt.show()
