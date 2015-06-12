# -*- coding: utf-8 -*-
"""
Simple script comparing two files, one with CsPad common mode, the other without
"""

import matplotlib.pyplot as plt
import h5py

import sys
XPP_LIB = "../xpp/utilities/"
sys.path.append(XPP_LIB)
import plot_utilities as pu
from images_processor import ImagesProcessor


DIR = "/reg/d/psdm/xpp/xpph6015/"
fname = "hdf5/xpph6015-r0077.h5"
fname_cm = "ftc/xtcav/Run0077.h5"

dset_main = "/Configure:0000/Run:0000/CalibCycle:0000/"
cspad_n = 0
cspad_dset = "CsPad2x2::ElementV1/XppGon.0:Cspad2x2.%d" % cspad_n

f = h5py.File(DIR + fname, "r")
f_cm = h5py.File(DIR + fname_cm, "r")

ip = ImagesProcessor()
# setting the dataset
ip.set_dataset(dset_main + cspad_dset)
ip.set_images_iterator("images_iterator_cspad140")
ip.add_analysis('get_histo_counts')
ip.add_analysis('get_mean_std')

ip.add_analysis("get_projection", args={'axis': 1})
# running the analyses
results = ip.analyze_images(DIR + fname, n=1000)
results_cm = ip.analyze_images(DIR + fname_cm, n=1000)

# plot the results
images_mean = results["get_mean_std"]["images_mean"]
h0 = results["get_histo_counts"]
images_mean_cm = results_cm["get_mean_std"]["images_mean"]
h0_cm = results_cm["get_histo_counts"]

pu.plot_image_and_proj(images_mean, title="CsPad #%d" % cspad_n)
pu.plot_image_and_proj(images_mean_cm, title="CsPad #%d, common mode" % cspad_n)

# a separate plot for histos
plt.figure()
plt.subplot(121)
plt.title("CsPad 140 #%d" % cspad_n)
plt.bar(h0["histo_bins"][:-1], h0["histo_counts"], width=5, log=True)
plt.subplot(122)
plt.title("CsPad 140 #%d common mode" % cspad_n)
plt.bar(h0_cm["histo_bins"][:-1], h0_cm["histo_counts"], width=5, log=True)

plt.figure()
plt.subplot(121)
plt.plot(images_mean.sum(axis=0), label="CsPad %d" % cspad_n)
plt.plot(images_mean_cm.sum(axis=0), label="CsPad Common Mode %d" % cspad_n)
plt.legend(loc='best')
plt.subplot(122)
plt.plot(images_mean.sum(axis=1), label="CsPad %d" % cspad_n)
plt.plot(images_mean_cm.sum(axis=1), label="CsPad Common Mode %d" % cspad_n)
plt.legend(loc='best')
plt.show()
