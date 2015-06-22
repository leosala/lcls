"""
Simple script to plot FEE spectrometer data
"""


import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import h5py
import numpy as np
import pandas as pd
import imp
from scipy.ndimage.measurements import center_of_mass


# import dictionary with useful XPP datasets
dset_names = imp.load_source('dset_names', 'xpp_datasets.py').dset_names

# load xpp libraries
import sys
XPP_LIB = "../xpp/utilities/"
sys.path.append(XPP_LIB)
import plot_utilities as pu
from images_processor import ImagesProcessor
import xpp_utilities as xpp

# checking arguments
if len(sys.argv) != 2:
    print "Usage: %s run_number" % sys.argv[0]
    sys.exit(-1)

# data filename
#DIR = "/reg/d/psdm/xpp/xpph6015/hdf5/"
# "Monitor datasets", without FEE images
DIR = "/reg/d/psdm/xpp/xpph6015/ftc/hdf5/"
run = int(sys.argv[1])
fname = DIR + "xpph6015-r%04d.h5" % run  # DIR + "xpph6015-r0005.h5"
print "Running on file %s" %fname

f = h5py.File(fname, 'r')
calib_cycle = 0

plot_fee_images = True
plot_down_images = True

# the root dataset
main_dsetname = "/Configure:0000/Run:0000/CalibCycle:%04d/" % calib_cycle

image_label = "Run %d, Calib %d" % (run, calib_cycle)

### Getting SASE spectra from FEE spectrometer
# getting the dataset and tags
fee_spectr, fee_tags = xpp.get_data_with_tags(fname, dset_names["FEE_spectr_hproj"], calib_cycle=calib_cycle)
fee_spectr = fee_spectr[:].astype('int32')
#down_spectr, down_tags = xpp.get_data_with_tags(fname, dset_names["Downstream_spectr_img"] + "/image")

try:
    fee_imgs = f[main_dsetname + dset_names["FEE_spectr_img"] + "/image"]
except:
    print "[WARNING] Images for FEE spectrometer cannot be found"
    plot_fee_images = False

try:
    down_imgs = f[main_dsetname + dset_names["Downstream_spectr_img"] + "/image"]
except:
    print "[WARNING] Images for Downstream spectrometer cannot be found"
    plot_down_images = False

# Starting the Images Processor for CsPad #0
ip = ImagesProcessor()
#dset_name = dset_names["FEE_spectr_img"]  #"CsPad2x2::ElementV1/XppGon.0:Cspad2x2.0"
# setting the dataset
#ip.set_dataset(main_dsetname + dset_name)
# addind the analysis
#ip.add_analysis('get_mean_std')
#ip.add_analysis('get_projection')
# special image iterator (CsPad140 needs some special care)
#ip.set_images_iterator('images_iterator_cspad140')
# run the analysis
#results = ip.analyze_images(fname, )

dset_name = dset_names["Downstream_spectr_img"]  #"CsPad2x2::ElementV1/XppGon.0:Cspad2x2.0"
ip.set_dataset(main_dsetname + dset_name)
ip.add_preprocess('set_roi', args={'roi': [[0, 1024], [440, 580]]})
ip.add_analysis('get_mean_std')
ip.add_analysis('get_projection', args={"axis": 1})
results_down = ip.analyze_images(fname, )

#pu.plot_image_and_proj(down_spectr[:].sum(axis=0), title="Downstream spectr %s (sum)" % run)

tags_mask = np.in1d(results_down["tags"], fee_tags)
down_filtered = results_down['get_projection']['spectra'][tags_mask]
#fee_spectr = results['get_projection']['spectra']
plt.figure()
plt.title("FEE img proj, %s" % image_label)
for i in range(3):
    plt.plot(fee_spectr[i])

plt.figure()
plt.title("Down img proj, %s" % image_label)
for i in range(3):
    plt.plot(down_filtered[i])

plt.figure()
plt.title("FEE spectra sum, %s" % image_label)
plt.plot(fee_spectr.sum(axis=0))

plt.figure()
plt.title("Downstream spectra sum, %s" % image_label)
plt.plot(down_filtered.sum(axis=0))


if plot_fee_images:
    pu.plot_image_and_proj(fee_imgs[0], title=("FEE %s" % image_label))
if plot_down_images:
    pu.plot_image_and_proj(down_imgs[1], title=("Downstream spectrometer %s" % image_label))

#down_sp = results_down['get_projection']['spectra'][18]
#fee_sp = results['get_projection']['spectra'][0]
#down_sp = down_sp - down_sp[0]
#fee_sp = fee_sp - fee_sp[0]
#down_energy = 8381. - 0.108 * np.arange(1, down_sp.shape[0] + 1)
#fee_energy = 8365. - 0.04 * np.arange(1, fee_sp.shape[0] + 1)

plt.show()

