# -*- coding: utf-8 -*-
"""
Created on Tue May 26 16:16:34 2015

@author: sala
"""

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

import sys
XPP_LIB = "../utilities/"
sys.path.append(XPP_LIB)
import plot_utilities as pu
from images_processor import ImagesProcessor

if len(sys.argv) != 2:
    print "Usage: %s filename" % sys.argv[0]
    sys.exit(-1)


DIR = "/reg/d/psdm/XPP/xpph6015/hdf5/"
#fname = DIR + "cxi61812-r0196.h5"
run = sys.argv[1].split("-")[-1].split(".")[0]
fname = DIR + sys.argv[1]  # "xpph6015-r0002.h5"

# the dataset path common to everything:
dset_main = "/Configure:0000/Run:0000/CalibCycle:0000/"

# Starting the Images Processor for CsPad #0
ip = ImagesProcessor()
dset_name = "CsPad2x2::ElementV1/XppGon.0:Cspad2x2.0"
# setting the dataset
ip.set_dataset(dset_main + dset_name)
# addind the analysis
ip.add_analysis('get_mean_std')
ip.add_analysis('get_histo_counts')
# special image iterator (CsPad140 needs some special care)
ip.set_images_iterator('images_iterator_cspad140')
# run the analysis
results = ip.analyze_images(fname, )

# plot the results
images_mean = results["get_mean_std"]["images_mean"]
h0 = results["get_histo_counts"]
pu.plot_image_and_proj(images_mean, title="CsPad #0")
plt.savefig("%s_cspad_0.png" % run)

# Do the same for CsPad #1
dset_name = "CsPad2x2::ElementV1/XppGon.0:Cspad2x2.1"
ip.set_dataset(dset_main + dset_name)
results = ip.analyze_images(fname, )
images_mean = results["get_mean_std"]["images_mean"]
h1 = results["get_histo_counts"]
pu.plot_image_and_proj(images_mean, title="CsPad #1")
plt.savefig("%s_cspad_1.png" % run)

# a separate plot for histos
plt.figure()
plt.subplot(121)
plt.title("CsPad 140 #0")
plt.bar(h0["histo_bins"][:-1], h0["histo_counts"], width=5, log=True)
plt.subplot(122)
plt.title("CsPad 140 #1")
plt.bar(h1["histo_bins"][:-1], h1["histo_counts"], width=5, log=True)
plt.savefig("%s_cspad_histos.png" % run)

#And now the Downstream spectrometer
opal_0 = dset_main + "/Camera::FrameV1/XppEndstation.0:Opal1000.0"
ip.set_dataset(opal_0)
# setting back the standard images iterator
ip.set_images_iterator('images_iterator')
results_opal = ip.analyze_images(fname)
images_mean = results_opal["get_mean_std"]["images_mean"]
h = results_opal["get_histo_counts"]
pu.plot_image_and_proj(images_mean, title="Opal #0")
plt.savefig("%s_opal_0.png" % run)

plt.figure()
plt.title("FEE img proj, %s" % run)
for i in range(3):
    plt.plot(results['get_projection']['spectra'][i])

plt.tight_layout()
plt.show()
