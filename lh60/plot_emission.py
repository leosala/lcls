# -*- coding: utf-8 -*-
"""
Plots emission spectra from CsPad data
It applies (if wanted):
+ ADU thresholds
+ dark background corrections
+ bad pixels map
+ ROIs
"""

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import h5py
import numpy as np

from miscellanea import interpolate_pixel_hline

import sys
XPP_LIB = "../xpp/utilities/"
sys.path.append(XPP_LIB)
import plot_utilities as pu
from images_processor import ImagesProcessor

if len(sys.argv) != 2:
    print "Usage: %s filename" % sys.argv[0]
    sys.exit(-1)


DIR = "/reg/d/psdm/XPP/xpph6015/hdf5/"
DIR = "/reg/d/psdm/xpp/xpph6015/ftc/hdf5/"

#roi0 = [[147, 155], [0, 391]]
#roi1 = [[155, 172], [0, 391]]
roi0 = [[0, 388], [157, 168]]
roi1 = [[0, 388], [165, 180]]

# events to be analyzed
n_events = 1000

# ADU thresholds
adu_low_thr_0 = 20.
adu_low_thr_1 = 20.

# dark background
dark_f = h5py.File("data/dark_run0030.h5", "r")
dark0 = dark_f['CsPad0/mean'][:]
dark1 = dark_f['CsPad1/mean'][:]

# bad pixels maps
bad_f = h5py.File("data/bad_pixels_r129_gt4.h5", "r")
bad_pixel_mask0 = bad_f['CsPad0/bad_pixel_mask'][:]
bad_pixel_mask1 = bad_f['CsPad1/bad_pixel_mask'][:]

#fname = DIR + "cxi61812-r0196.h5"
run = int(sys.argv[1])
fname = DIR + "xpph6015-r%04d.h5" % run  # DIR + "xpph6015-r0005.h5"
print "Running on %s" %fname

image_label = "Run %d" % run
# the dataset path common to everything:
dset_main = "/Configure:0000/Run:0000/CalibCycle:0000/"

# Starting the Images Processor for CsPad #0
ip = ImagesProcessor()
dset_name = "CsPad2x2::ElementV1/XppGon.0:Cspad2x2.0"
ip.set_dataset(dset_main + dset_name)
# addind the analysis
ip.add_preprocess("subtract_correction", args={'sub_image': dark0})
ip.add_preprocess("set_thr", args={"thr_low": adu_low_thr_0})
ip.add_preprocess("correct_bad_pixels", args={"mask": bad_pixel_mask0})
ip.add_preprocess(interpolate_pixel_hline, args={"hpixel": 193})
#ip.add_preprocess("set_roi", args={'roi': roi0})
ip.add_analysis('get_mean_std')
ip.add_analysis('get_histo_counts')
ip.add_analysis('get_projection', args={'axis': 1, })  # "thr_low": 20, })
# special image iterator (CsPad140 needs some special care)
ip.set_images_iterator('images_iterator_cspad140')
# run the analysis
results0 = ip.analyze_images(fname, n=n_events)

dset_name = "CsPad2x2::ElementV1/XppGon.0:Cspad2x2.1"
ip.set_dataset(dset_main + dset_name)
# addind the analysis
ip.add_preprocess("subtract_correction", args={'sub_image': dark1})
ip.add_preprocess("set_thr", args={"thr_low": adu_low_thr_1})
ip.add_preprocess("correct_bad_pixels", args={"mask": bad_pixel_mask1})
ip.add_preprocess(interpolate_pixel_hline, args={"hpixel": 193})
#ip.add_preprocess("set_roi", args={'roi': roi1})
ip.add_analysis('get_mean_std')
ip.add_analysis('get_histo_counts')
ip.add_analysis('get_projection', args={'axis': 1, })  # "thr_low": 20, })
# special image iterator (CsPad140 needs some special care)
ip.set_images_iterator('images_iterator_cspad140')
# run the analysis
results1 = ip.analyze_images(fname, n=n_events)


# plot the results
images_mean0 = results0["get_mean_std"]["images_mean"]
images_mean1 = results1["get_mean_std"]["images_mean"]
pu.plot_image_and_proj(images_mean0, title="CsPad #0 %s" % image_label)
pu.plot_image_and_proj(images_mean1, title="CsPad #1 %s" % image_label)

# a separate plot for histos
h0 = results0["get_histo_counts"]
h1 = results1["get_histo_counts"]
plt.figure()
plt.subplot(121)
plt.title("CsPad 140 #0")
plt.bar(h0["histo_bins"][:-1], h0["histo_counts"], width=5, log=True)
plt.axvline(25)
plt.subplot(122)
plt.title("CsPad 140 #1")
plt.bar(h1["histo_bins"][:-1], h1["histo_counts"], width=5, log=True)
plt.axvline(22)

# spectra
plt.figure()
plt.title("projection CsPad #0 %s" % image_label)
plt.plot(results0["get_projection"]["spectra"].sum(axis=0))

plt.figure()
plt.title("projection CsPad #1 %s" % image_label)
plt.plot(results1["get_projection"]["spectra"].sum(axis=0))

plt.show()
