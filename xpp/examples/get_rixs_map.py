import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import h5py
import numpy as np
import pandas as pd
import imp

# import dictionary with useful XPP datasets
dset_names = imp.load_source('dset_names', '../scripts/xpp_datasets.py').dset_names

# load xpp libraries
import sys
XPP_LIB = "../utilities/"
sys.path.append(XPP_LIB)
import plot_utilities as pu
from images_processor import ImagesProcessor
import xpp_utilities as xpp

# FEE spectrometer filtering
x_low = 100  # n pixels to check for no signal, from left
x_hi = x_low  # n pixels to check for no signal, from right
thr = 100000  # threshold on sum of counts in each of the outlier areas

# checking arguments
if len(sys.argv) != 2:
    print "Usage: %s filename" % sys.argv[0]
    sys.exit(-1)

# data filename
fname = sys.argv[1]  # DIR + "xpph6015-r0005.h5"

# the root dataset
main_dsetname = "/Configure:0000/Run:0000/CalibCycle:0000/"

### Getting SASE spectra from FEE spectrometer
# getting the dataset and tags
fee_spectr, fee_tags = xpp.get_data_with_tags(fname, dset_names["FEE_spectr_hproj"])

# getting a boolean mask of events with no data on the ouside regions of the
# FEE spectrometer
fee_mask = np.ones(fee_tags.shape, dtype=bool)
fee_spectra_data = fee_spectr[:]
for i in range(fee_tags.shape[0]):
    if fee_spectra_data[i][: x_low].sum() > thr or fee_spectra_data[i][-x_hi:].sum() > thr:
        fee_mask[i] = False

### getting the spectra from CsPads
# loading the ImagesProcessor class
ip = ImagesProcessor()
# setting the dataset
ip.set_dataset(main_dsetname + "CsPad2x2::ElementV1/XppGon.0:Cspad2x2.0")
# setting the special image iterator for the CsPad140
ip.set_images_iterator("images_iterator_cspad140")
# adding the analyses
ip.add_analysis("get_projection", args={'axis': 1})
ip.add_analysis("get_histo_counts")
# running the analyses
results = ip.analyze_images(fname)

### getting the RIXS map
cspad0_histo = results["get_histo_counts"]
cspad0_spectra = results["get_projection"]["spectra"]
cspad0_tags = results["tags"]
# creating a boolean mask with the intersection of tags from cspad and fee
tags_mask = np.in1d(cspad0_tags, fee_tags[fee_mask], assume_unique=True)

# produce RIXS map
emission_spectra = np.dot(np.linalg.pinv(cspad0_spectra), fee_spectra_data)
# finally plotting
pu.plot_image_and_proj(emission_spectra, title="RIXS map")
# also the histos
plt.figure()
plt.title("CsPad #0 counts histo")
plt.bar(cspad0_histo['histo_bins'][:-1], cspad0_histo['histo_counts'],
        width=cspad0_histo['histo_bins'][1] - cspad0_histo['histo_bins'][0] )
plt.show()
