# -*- coding: utf-8 -*-
"""
Script to plot and save to HDF5 dark correction and (eventually) bad pixels map
"""

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import h5py
import sys

# importing the dedicated XPP libraries
XPP_LIB = "../xpp/utilities/"
sys.path.append(XPP_LIB)
import plot_utilities as pu
from images_processor import ImagesProcessor

# do bad pixel map?
do_bad_pixels = True
# if so, which value to use for defining it a bad pixel?
bad_pixel_thr = 6.5

# data directories
#DIR = "/reg/d/psdm/XPP/xpph6015/hdf5/"
DIR = "/reg/d/psdm/xpp/xpph6015/ftc/hdf5/"

# number of events to be analyzed
n_events = -1  #2000

if len(sys.argv) != 2:
    print "Usage: %s run_number" % sys.argv[0]
    sys.exit(-1)

run = int(sys.argv[1])
fname = DIR + "xpph6015-r%04d.h5" % run  # DIR + "xpph6015-r0005.h5"
print "Running on %s" %fname

image_label = "Run %d" % run

# the dataset path common to everything
# usually per file there is only one run/calibcycle, but this could change
dset_main = "/Configure:0000/Run:0000/CalibCycle:0000/"

# Starting the Images Processor for CsPad #0
ip = ImagesProcessor()
dset_name = "CsPad2x2::ElementV1/XppGon.0:Cspad2x2.0"
ip.set_dataset(dset_main + dset_name)
# addind the analysis
ip.add_analysis('get_mean_std')
ip.add_analysis('get_histo_counts')
# special image iterator (CsPad140 needs some special care)
ip.set_images_iterator('images_iterator_cspad140')
# run the analysis
results0 = ip.analyze_images(fname, n=n_events)

dset_name = "CsPad2x2::ElementV1/XppGon.0:Cspad2x2.1"
ip.set_dataset(dset_main + dset_name)
# addind the analysis
ip.add_analysis('get_mean_std')
ip.add_analysis('get_histo_counts')
# special image iterator (CsPad140 needs some special care)
ip.set_images_iterator('images_iterator_cspad140')
# run the analysis
results1 = ip.analyze_images(fname, n=n_events)

# getting the needed quantities
images_mean0 = results0["get_mean_std"]["images_mean"]
images_mean1 = results1["get_mean_std"]["images_mean"]
images_std0 = results0["get_mean_std"]["images_std"]
images_std1 = results1["get_mean_std"]["images_std"]
h0 = results0["get_histo_counts"]
h1 = results1["get_histo_counts"]

# saving everything in an hdf5 file
if do_bad_pixels:
    out_f = h5py.File("badpixel_run%04d_gt%d.h5" %(run, bad_pixel_thr))
else:
    out_f = h5py.File("dark_run%04d.h5" %run)

dset = out_f.create_dataset("CsPad0/mean", data=images_mean0)
dset = out_f.create_dataset("CsPad1/mean", data=images_mean1)
if do_bad_pixels:
    dset = out_f.create_dataset("CsPad0/bad_pixel", data=(images_std0 > bad_pixel_thr))
    dset = out_f.create_dataset("CsPad1/bad_pixel", data=(images_std1 > bad_pixel_thr))

dset = out_f.create_dataset("CsPad0/std", data=images_std0)
dset = out_f.create_dataset("CsPad1/std", data=images_std1)
dset = out_f.create_dataset("CsPad0/histo_counts", data=h0["histo_counts"])
dset = out_f.create_dataset("CsPad0/histo_bins", data=h0["histo_bins"])
dset = out_f.create_dataset("CsPad1/histo_counts", data=h1["histo_counts"])
dset = out_f.create_dataset("CsPad1/histo_bins", data=h1["histo_bins"])

out_f.close()

# plot the results
pu.plot_image_and_proj(images_mean0, title="CsPad #0 %s" % image_label)
pu.plot_image_and_proj(images_mean1, title="CsPad #1 %s" % image_label)

# a separate plot for histos
plt.figure()
plt.subplot(121)
plt.title("CsPad 140 #0")
plt.bar(h0["histo_bins"][:-1], h0["histo_counts"], width=5, log=True)
plt.subplot(122)
plt.title("CsPad 140 #1")
plt.bar(h1["histo_bins"][:-1], h1["histo_counts"], width=5, log=True)

plt.show()
