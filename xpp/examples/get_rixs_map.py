import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import h5py
import numpy as np
import pandas as pd
import imp
from scipy.signal import savgol_filter

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
x_low = 200  # n pixels to check for no signal, from left
x_hi = 200  # n pixels to check for no signal, from right
thr = 8e-3  # threshold on sum of counts in each of the outlier areas
n_events = 10000

roi1 = [[0, 388], [155, 172]]

# from run 127
roi0 = [[0, 388], [150, 161]]
roi1 = [[0, 388], [105, 124]]

# checking arguments
if len(sys.argv) != 2:
    print "Usage: %s filename" % sys.argv[0]
    sys.exit(-1)


dark_f = h5py.File("../scripts/dark_run0030.h5", "r")
dark0 = dark_f['CsPad0/mean'][:]
dark1 = dark_f['CsPad1/mean'][:]

bad_f = h5py.File("../scripts/bad_pixels_r129_gt4.h5", "r")

bad_pixel_mask0 = bad_f['CsPad0/bad_pixel_mask'][:]
bad_pixel_mask1 = bad_f['CsPad1/bad_pixel_mask'][:]


fee_response_coeff = [3.06012545e-04,  -1.48236282e+00,   1.67440870e+03, -1.40806046e+04]
fee_response =  np.poly1d(fee_response_coeff)(range(2048+2))
fee_response /= fee_response.max()
fee_response[fee_response < 0 ] = 1
# data filename
fname = sys.argv[1]  # DIR + "xpph6015-r0005.h5"

# the root dataset
main_dsetname = "/Configure:0000/Run:0000/CalibCycle:0000/"

### Getting SASE spectra from FEE spectrometer
# getting the dataset and tags
fee_spectr, fee_tags = xpp.get_data_with_tags(fname, dset_names["FEE_spectr_hproj"], )

# getting a boolean mask of events with no data on the ouside regions of the
# FEE spectrometer
fee_mask2 = np.ones(fee_tags[:n_events].shape, dtype=bool)
fee_spectra_data2 = fee_spectr[:n_events].astype('int32')
fee_spectra_data = fee_spectra_data2[:, :-10].astype('float').copy()

#fee_spectra_norm = fee_spectra_data.max(axis=1)
for i in range(fee_spectra_data.shape[0]):
    fee_spectra_data[i, :] = np.divide(fee_spectra_data[i, :], fee_response[:-10])
    norm = fee_spectra_data[i, :].sum()
    if norm == 0:
        fee_mask2[i] = False
    else:
        fee_spectra_data[i, :] = np.divide(fee_spectra_data[i, :], norm)
        #fee_spectra_data[i, :] = np.divide(fee_spectra_data[i, :], fee_response[:-10])
        fee_spectra_data[i, :] = savgol_filter(fee_spectra_data[i], 11, 2)

for i in range(fee_tags[:n_events].shape[0]):
    mymax = fee_spectra_data[i].max()
    if fee_spectra_data[i][: x_low].max() / mymax > thr or fee_spectra_data[i][-x_hi:].max() / mymax > thr:
        fee_mask2[i] = False

df_i0 = xpp.get_scalar_data(fname, ["Bld::BldDataFEEGasDetEnergyV1/FEEGasDetEnergy/data", 
                                    "Ipimb::DataV2/XppEnds_Ipm0/data"], n_events=n_events)
                    
i0 = df_i0['Bld::BldDataFEEGasDetEnergyV1/FEEGasDetEnergy/data.f_11_ENRC'].loc[fee_tags[:n_events]]
i0 = i0[i0 > 1.3]
tags_i0 = i0.index.tolist()
fee_mask = fee_mask2 * np.in1d(fee_tags[:n_events], tags_i0)

### getting the spectra from CsPads
# loading the ImagesProcessor class
ip = ImagesProcessor()
# setting the dataset
ip.set_dataset(main_dsetname + "CsPad2x2::ElementV1/XppGon.0:Cspad2x2.1")
ip.add_preprocess("subtract_correction", args={'sub_image': dark1})
ip.add_preprocess("set_thr", args={"thr_low": 20})
ip.add_preprocess("correct_bad_pixels", args={"mask": bad_pixel_mask1})
ip.add_preprocess("set_roi", args={'roi': roi1})
ip.set_images_iterator("images_iterator_cspad140")
ip.add_analysis("get_projection", args={'axis': 1})
# running the analyses
results = ip.analyze_images(fname, n_events)

### getting the RIXS map
#cspad0_histo = results["get_histo_counts"]
cspad0_spectra = results["get_projection"]["spectra"]
for i in range(cspad0_spectra.shape[0]):
    cspad0_spectra[i] = savgol_filter(cspad0_spectra[i], 11, 2)
cspad0_spectra[cspad0_spectra<0] = 0
    
cspad0_tags = results["tags"]
# creating a boolean mask with the intersection of tags from cspad and fee
tags_mask = np.in1d(cspad0_tags, fee_tags[fee_mask], assume_unique=True)

# produce RIXS map
#cspad0_spectra[cspad0_spectra < 0] = 0
#emission_spectra = np.dot(np.linalg.pinv(cspad0_spectra), fee_spectra_data)
inv = np.linalg.pinv(fee_spectra_data[tags_mask][:, :1500], rcond=1e-3)
emission_spectra = np.dot(inv, cspad0_spectra[tags_mask][:, 200:300])
print cspad0_spectra[tags_mask].shape

# finally plotting
pu.plot_image_and_proj(cspad0_spectra[tags_mask], title="Emission spectra map")
pu.plot_image_and_proj(fee_spectra_data[tags_mask], title="FEE spectra map")
pu.plot_image_and_proj(inv, title="FEE pseudo inverse")
pu.plot_image_and_proj(emission_spectra, title="RIXS map")
# also the histos
#plt.figure()
#plt.title("CsPad #0 counts histo")
#plt.bar(cspad0_histo['histo_bins'][:-1], cspad0_histo['histo_counts'],
#        width=cspad0_histo['histo_bins'][1] - cspad0_histo['histo_bins'][0] )
plt.show()
