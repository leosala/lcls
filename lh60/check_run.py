"""
Script to check basic run quantities, with:
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


def interpolate_pixel_hline(image, pixel_pos, axis=0, method="mean"):
    """

    Parameters
    ----------
    image: Numpy array
        the input array image
    hpixels: int
        the pixel line to be interpolated


    Returns
    -------
    image: Numpy array
        the image, with subtraction applied
    """
    if axis == 0:
        image[pixel_pos] = (image[pixel_pos - 1] + image[pixel_pos + 1]) / 2
    else:
        image[:, pixel_pos] = (image[:, pixel_pos - 1] + image[:, pixel_pos + 1]) / 2
    return image


# import dictionary with useful XPP datasets
from xpp_datasets import dset_names
dset_names["IPM0"] = "Lusi::IpmFexV1/XppEnds_Ipm0/data"

# load xpp libraries
import sys
XPP_LIB = "../xpp/utilities/"
sys.path.append(XPP_LIB)
import plot_utilities as pu
from images_processor import ImagesProcessor
import xpp_utilities as xpp

n_events = 2000
# CsPad ROIs 
# from run 127 till run XXXX
roi0 = [[0, 388], [150, 161]]
roi1 = [[0, 388], [105, 124]]

# data quality cuts
#fee_i0 = 1.0
#ch2_i0 = 0.1
#ch2_i0 = 0.1

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

# getting quantities for checks
# I0 Gas monitor
df_i0 = xpp.get_scalar_data(fname, ["Bld::BldDataFEEGasDetEnergyV1/FEEGasDetEnergy/data", ] )
i0 = df_i0['Bld::BldDataFEEGasDetEnergyV1/FEEGasDetEnergy/data.f_11_ENRC'].loc[fee_tags[:n_events]]
# IPM0 CH2
ipm0, ipm0_tags = xpp.get_data_with_tags(fname, dset_names["IPM0"])
i0_ch2 = ipm0["channel"][:, 2]

### getting the spectra from CsPads
# loading the ImagesProcessor class
ip = ImagesProcessor()
# setting the dataset
ip.set_dataset(main_dsetname + "CsPad2x2::ElementV1/XppGon.0:Cspad2x2.1")
ip.add_preprocess("subtract_correction", args={'sub_image': dark1})
ip.add_preprocess("set_thr", args={"thr_low": 22})
ip.add_preprocess("correct_bad_pixels", args={"mask": bad_pixel_mask1})
ip.add_preprocess(interpolate_pixel_hline, args={"pixel_pos": 193})
ip.add_preprocess("set_roi", args={'roi': roi1})
ip.set_images_iterator("images_iterator_cspad140")
ip.add_analysis("get_projection", args={'axis': 1})
ip.add_analysis("get_mean_std", )
# running the analyses
results = ip.analyze_images(fname, n_events, )

### getting the RIXS map
cspad0_spectra = results["get_projection"]["spectra"]
cspad0_tags = results["tags"]
cspad0_mean = results["get_mean_std"]["images_mean"]
sase = fee_spectra_data

plt.figure()
plt.subplot(121)
plt.title("Run %d" % run)
plt.plot(i0_ch2, ".", )
plt.ylabel("FEEGasDet.f11")
plt.subplot(122)
plt.hist(i0_ch2, bins=100)

plt.figure()
plt.subplot(121)
plt.title("Run %d" % run)
plt.plot(i0, ".", )
plt.ylabel("IPM0 Ch2")
plt.subplot(122)
plt.hist(i0.tolist(), bins=100)

# finally plotting
pu.plot_image_and_proj(cspad0_spectra, title="Emission spectra map")
pu.plot_image_and_proj(sase, title="FEE spectra map")
pu.plot_image_and_proj(cspad0_mean, title="Average CsPad#0")


plt.tight_layout()
plt.show()

