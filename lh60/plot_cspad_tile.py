"""
Script to quickly analyze CsPad140k images of a run.
It produces:
+ ADU histograms per CsPad140k tile
+ Image average and projections per tile
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

# checking arguments
if len(sys.argv) != 2:
    print "Usage: %s run_number" % sys.argv[0]
    sys.exit(-1)

# data directory
#DIR = "/reg/d/psdm/xpp/xpph6015/hdf5/"
DIR = "/reg/d/psdm/xpp/xpph6015/ftc/hdf5/"

# setting the filename
run = int(sys.argv[1])
fname = DIR + "xpph6015-r%04d.h5" % run  # DIR + "xpph6015-r0005.h5"
print "Running on %s" %fname

## CsPad#0
# name of the CsPad dataset (always relative to the Calib/run/ etc main dataset)
cspad0_name = "CsPad2x2::ElementV1/XppGon.0:Cspad2x2.0/data"
# get data and tags of the CsPad. In this case, no glueing is performed
cspad0_data, cspad0_tags = xpp.get_data_with_tags(fname, cspad0_name)
# create histograms
h0, h0_bins = np.histogram(cspad0_data[:][:, :,:,0], bins=np.arange(-100, 1000, 5))
h1, h1_bins = np.histogram(cspad0_data[:][:, :,:,1], bins=np.arange(-100, 1000, 5))

# plot!
fig = plt.figure()
plt.subplot(121)
plt.title("CsPad#0 tile 0")
plt.bar(h0_bins[:-1], h0, width=h0_bins[1] - h0_bins[0], log=True)
plt.subplot(122)
plt.title("CsPad#0 tile 1")
plt.bar(h1_bins[:-1], h1, width=h1_bins[1] - h1_bins[0], log=True)

pu.plot_image_and_proj(cspad0_data[:][:,:,:,0].sum(axis=0), title="CsPad#0 tile 0")
pu.plot_image_and_proj(cspad0_data[:][:,:,:,1].sum(axis=0), title="CsPad#0 tile 1")

## CsPad#1
# name of the CsPad dataset (always relative to the Calib/run/ etc main dataset)
cspad1_name = "CsPad2x2::ElementV1/XppGon.0:Cspad2x2.1/data"
# get data and tags of the CsPad. In this case, no glueing is performed
cspad1_data, cspad1_tags = xpp.get_data_with_tags(fname, cspad1_name)
# create histograms
h0, h0_bins = np.histogram(cspad1_data[:][:, :,:,0], bins=np.arange(-100, 1000, 5))
h1, h1_bins = np.histogram(cspad1_data[:][:, :,:,1], bins=np.arange(-100, 1000, 5))

# plot!
fig = plt.figure()
plt.subplot(121)
plt.title("CsPad#1 tile 0")
plt.bar(h0_bins[:-1], h0, width=h0_bins[1] - h0_bins[0], log=True)
plt.subplot(122)
plt.title("CsPad#1 tile 1")
plt.bar(h1_bins[:-1], h1, width=h1_bins[1] - h1_bins[0], log=True)

pu.plot_image_and_proj(cspad1_data[:][:,:,:,0].sum(axis=0), title="CsPad#1 tile 0")
pu.plot_image_and_proj(cspad1_data[:][:,:,:,1].sum(axis=0), title="CsPad#1 tile 1")

#plt.tight_layout()
plt.show()
