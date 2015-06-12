"""
Script to create the SASE and emission maps, with proper:
+ dark background correction
+ bad pixels map
+ data quality cuts
"""

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import h5py
import numpy as np
import pandas as pd
import imp
from scipy.signal import savgol_filter


### TO BE CHECKED, DO NOT USE IT YET

# import dictionary with useful XPP datasets
#dset_names = imp.load_source('dset_names', '../scripts/xpp_datasets.py').dset_names
from xpp_datasets import dset_names
dset_names["IPM0"] = "Lusi::IpmFexV1/XppEnds_Ipm0/data"

# load xpp libraries
import sys
XPP_LIB = "../xpp/utilities/"
sys.path.append(XPP_LIB)
import plot_utilities as pu
from images_processor import ImagesProcessor
import xpp_utilities as xpp

n_events = 500

# CsPad ROIs 
# from run 127 till run XXXX
roi0 = [[0, 388], [150, 161]]
roi1 = [[0, 388], [105, 124]]

# data quality cuts
fee_i0 = 1.0
ch2_i0 = 0.1

# checking arguments
if len(sys.argv) != 2:
    print "Usage: %s filename" % sys.argv[0]
    sys.exit(-1)


# Dark background corrections
dark_f = h5py.File("../scripts/dark_run0030.h5", "r")
dark0 = dark_f['CsPad0/mean'][:]
dark1 = dark_f['CsPad1/mean'][:]

# Bad pixels map
bad_f = h5py.File("../scripts/bad_pixels_r129_gt4.h5", "r")
bad_pixel_mask0 = bad_f['CsPad0/bad_pixel_mask'][:]
bad_pixel_mask1 = bad_f['CsPad1/bad_pixel_mask'][:]

# data filename
fname = sys.argv[1]  # DIR + "xpph6015-r0005.h5"
run = fname.split("-")[-1].split(".")[0]
# the root dataset
main_dsetname = "/Configure:0000/Run:0000/CalibCycle:0000/"

### Getting SASE spectra from FEE spectrometer
# getting the dataset and tags
fee_spectr, fee_tags = xpp.get_data_with_tags(fname, dset_names["FEE_spectr_hproj"], )

# getting a boolean mask of events with no data on the ouside regions of the
# FEE spectrometer
fee_mask = np.ones(fee_tags[:n_events].shape, dtype=bool)
fee_spectra_data = fee_spectr[:].astype('int32')

# getting quantities for data quality cuts
df_i0 = xpp.get_scalar_data(fname, ["Bld::BldDataFEEGasDetEnergyV1/FEEGasDetEnergy/data", 
                                    "Ipimb::DataV2/XppEnds_Ipm0/data"], )
                    
i0 = df_i0['Bld::BldDataFEEGasDetEnergyV1/FEEGasDetEnergy/data.f_11_ENRC'].loc[fee_tags[:n_events]]
ipm0, ipm0_tags = xpp.get_data_with_tags(fname, dset_names["IPM0"])
i0_ch2 = ipm0["channel"][:,2]

i0_mask = np.array((i0 > fee_i0).tolist())
i0_ch2_mask = i0_ch2 > ch2_i0
tags_i0 = np.array(i0.index.tolist())

cond_mask = np.in1d(tags_i0[i0_mask], ipm0_tags[i0_ch2_mask])
cond_tags = tags_i0[cond_mask]

fee_tags_mask = fee_mask * np.in1d(fee_tags[:n_events], cond_tags, assume_unique=True)
holy_tags = fee_tags[fee_tags_mask]

### getting the spectra from CsPads
# loading the ImagesProcessor class
ip = ImagesProcessor()
# setting the dataset
ip.set_dataset(main_dsetname + "CsPad2x2::ElementV1/XppGon.0:Cspad2x2.1")
ip.add_preprocess("subtract_correction", args={'sub_image': dark1})
ip.add_preprocess("set_thr", args={"thr_low": 22})
ip.add_preprocess("correct_bad_pixels", args={"mask": bad_pixel_mask1})
ip.add_preprocess("set_roi", args={'roi': roi1})
ip.set_images_iterator("images_iterator_cspad140")
ip.add_analysis("get_projection", args={'axis': 1})
# running the analyses
results = ip.analyze_images(fname, n_events)

### getting the RIXS map
cspad0_spectra = results["get_projection"]["spectra"]
cspad0_tags = results["tags"]
# creating a boolean mask with the intersection of tags from cspad and fee
cspad_tags_mask = np.in1d(cspad0_tags, holy_tags, assume_unique=True)
fee_tags_mask = np.in1d(holy_tags, cspad0_tags, assume_unique=True)

# dump maps in ASCII file
np.savetxt("%s_sase.gz" % run, fee_spectra_data[fee_tags_mask])
np.savetxt("%s_cspad1_emission.gz" % run, fee_spectra_data[cspad_tags_mask])

# produce RIXS map
#cspad0_spectra[cspad0_spectra < 0] = 0
#emission_spectra = np.dot(np.linalg.pinv(cspad0_spectra), fee_spectra_data)

# finally plotting
pu.plot_image_and_proj(cspad0_spectra[cspad_tags_mask], title="Emission spectra map")
pu.plot_image_and_proj(fee_spectra_data[fee_tags_mask], title="FEE spectra map")
plt.show()
