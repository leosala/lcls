"""
Script to create the SASE and emission maps, with proper:
+ dark background correction
+ bad pixels map
+ data quality cuts
"""
import sys
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import h5py
import numpy as np
import pandas as pd
import imp
from scipy.signal import savgol_filter

# import dictionary with useful XPP datasets
#dset_names = imp.load_source('dset_names', '../scripts/xpp_datasets.py').dset_names
from xpp_datasets import dset_names
dset_names["IPM0"] = "Lusi::IpmFexV1/XppEnds_Ipm0/data"

from miscellanea import interpolate_pixel_hline

# load xpp libraries
import sys
XPP_LIB = "../xpp/utilities/"
sys.path.append(XPP_LIB)
import plot_utilities as pu
from images_processor import ImagesProcessor
import xpp_utilities as xpp


# Normalize spectra with Ch2?
normalize = True

# number of events to be analyzed
n_events = -1

# CsPad ROIs 
# from run 127 till run XXXX
roi0 = [[0, 388], [150, 161]]
roi1 = [[0, 388], [105, 124]]

# data quality cuts
fee_i0 = 1.0
ch2_i0 = 0.2

# checking arguments
if len(sys.argv) != 2:
    print "Usage: %s filename" % sys.argv[0]
    sys.exit(-1)


# Dark background corrections
dark_f = h5py.File("data/dark_run0030.h5", "r")
dark0 = dark_f['CsPad0/mean'][:]
dark1 = dark_f['CsPad1/mean'][:]

# Bad pixels map
bad_f = h5py.File("data/bad_pixels_r129_gt4.h5", "r")
bad_pixel_mask0 = bad_f['CsPad0/bad_pixel_mask'][:]
bad_pixel_mask1 = bad_f['CsPad1/bad_pixel_mask'][:]

# data filename
DIR = "/reg/d/psdm/XPP/xpph6015/hdf5/"
DIR = "/reg/d/psdm/xpp/xpph6015/ftc/hdf5/"
run = int(sys.argv[1])
fname = DIR + "xpph6015-r%04d.h5" % run  # DIR + "xpph6015-r0005.h5"
print "Running on %s" %fname

# the root dataset
main_dsetname = "/Configure:0000/Run:0000/CalibCycle:0000/"

### Getting SASE spectra from FEE spectrometer
# getting the dataset and tags
fee_spectr, fee_tags = xpp.get_data_with_tags(fname, dset_names["FEE_spectr_hproj"], )

# getting a boolean mask of events, and the data
fee_mask = np.ones(fee_tags[:n_events].shape, dtype=bool)
# remove the very last two pixels, which sometimes are crazy possibly because of calibration procedure
fee_spectra_data = fee_spectr.value[:, :-2].astype('int32')

# getting quantities for data quality cuts
df_i0 = xpp.get_scalar_data(fname, ["Bld::BldDataFEEGasDetEnergyV1/FEEGasDetEnergy/data", 
                                    "Ipimb::DataV2/XppEnds_Ipm0/data"], )
                    
i0 = df_i0['Bld::BldDataFEEGasDetEnergyV1/FEEGasDetEnergy/data.f_11_ENRC'].loc[fee_tags[:n_events]]
ipm0, ipm0_tags = xpp.get_data_with_tags(fname, dset_names["IPM0"])
i0_ch2 = ipm0["channel"][:, 2]

i0_mask = np.array((i0 > fee_i0).tolist())
i0_ch2_mask = i0_ch2 > ch2_i0
tags_i0 = np.array(i0.index.tolist())

# getting a list of tags with the correct i0
cond_mask = np.in1d(tags_i0[i0_mask], ipm0_tags[i0_ch2_mask])
cond_tags = tags_i0[i0_mask][cond_mask]
#selected I0
i0_ch2_sel_mask = np.in1d(ipm0_tags[i0_ch2_mask], cond_tags)
i0_ch2_sel = i0_ch2[i0_ch2_mask][i0_ch2_sel_mask]

fee_tags_mask = fee_mask * np.in1d(fee_tags[:n_events], cond_tags, assume_unique=True)
holy_tags = fee_tags[:n_events][fee_tags_mask]
print "selected events: %d" % holy_tags.shape[0]
if holy_tags.shape[0] == 0:
    print "No events selected, exiting"
    sys.exit(-1)

### getting the spectra from CsPads
# loading the ImagesProcessor class
ip = ImagesProcessor()
# setting the dataset
ip.set_dataset(main_dsetname + "CsPad2x2::ElementV1/XppGon.0:Cspad2x2.1")
ip.add_preprocess("subtract_correction", args={'sub_image': dark1})
ip.add_preprocess("set_thr", args={"thr_low": 22})
ip.add_preprocess("correct_bad_pixels", args={"mask": bad_pixel_mask1})
ip.add_preprocess(interpolate_pixel_hline, args={"hpixel": 193})
ip.add_preprocess("set_roi", args={'roi': roi1})
ip.set_images_iterator("images_iterator_cspad140")
ip.add_analysis("get_projection", args={'axis': 1})
# running the analyses
results = ip.analyze_images(fname, n_events, tags=holy_tags)

### getting the RIXS map
print results["get_projection"].keys()
cspad0_spectra = results["get_projection"]["spectra"]
cspad0_tags = results["tags"]
# creating a boolean mask with the intersection of tags from cspad and fee
#cspad_tags_mask = np.in1d(cspad0_tags, holy_tags, assume_unique=True)
#fee_tags_mask = np.in1d(holy_tags, cspad0_tags, assume_unique=True)

# int64 conversion needed because of tags
sase = fee_spectra_data[fee_tags_mask].astype(np.float64)

# normalize sase, emission to I0
if normalize:
    sase = (sase.T / i0_ch2_sel).T
    cspad0_spectra = (cspad0_spectra.T / i0_ch2_sel).T

# create the maps with the proper tags

fee_map = np.insert(sase, 0,
                    fee_tags[fee_tags_mask].astype(np.int64), axis=1)
cspad_map = np.insert(cspad0_spectra.astype(np.int64), 0,
                      cspad0_tags.astype(np.int64), axis=1)

print "same tags?", (fee_tags[fee_tags_mask] == cspad0_tags).all()
# dump maps in ASCII file
np.savetxt("run%s_sase.gz" % run, fee_map, header="#tags\tpixels")
np.savetxt("run%s_cspad1_emission.gz" % run, cspad_map, header="#tags\tpixels")

# produce RIXS map
#cspad0_spectra[cspad0_spectra < 0] = 0
#sase /= sase.max()
#inv = np.linalg.pinv(sase)
#emission_spectra = np.dot(inv, cspad0_spectra)

# finally plotting
pu.plot_image_and_proj(cspad0_spectra, title="Emission spectra map run %d" %run)
pu.plot_image_and_proj(sase, title="FEE spectra map run %d" %run)
plt.show()

