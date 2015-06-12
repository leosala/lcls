# -*- coding: utf-8 -*-
"""
This script runs over a particular set of runs, used to calibrate the FEE spectrometer, and
then create a response function
"""

import sys
XPP_LIB = "../xpp/utilities/"
sys.path.append(XPP_LIB)
from xpp_datasets import dset_names
import xpp_utilities as xpp
import matplotlib.pyplot as plt
import scipy.signal
import numpy as np


DIR = "/reg/d/psdm/xpp/xpph6015/ftc/hdf5/"

# ordert of the response polynomial to be fitted
poly_order = 3

# x, y are the points we want to fit for the response envelope. Currently
# they are fitted with the max value
x = []
y = []

# eventual boundary conditions
x.append(0)
y.append(0)
#x.append(2048)
#y.append(0)

envelope = None

plt.figure()
# running on all runs ranging from 19 till 26
for run in range(19, 27):
    fname = DIR + "xpph6015-r00%d.h5" % run
    print "Running on file %s" %fname
    # getting the data
    df = xpp.get_scalar_data(fname, dset_names["FeeGasDet"])
    # getting I0
    i0 = np.array(df["FEEGasDetEnergy.f_11_ENRC"].tolist())
    # Getting FEE spectra
    fee_spectra, fee_tags = xpp.get_data_with_tags(fname, dset_names["FEE_spectr_hproj"])
    # normalization
    spectra = fee_spectra[:].astype('int32').sum(axis=0) / i0.sum()
    # filling x, y
    y.append(spectra.max())
    t = np.where(spectra == y[-1])
    x.append(t[0][0])
    # plotting 
    plt.plot(spectra, label="Run %d" %run)

# creating the envelope
envelope = np.poly1d(np.polyfit(x, y, poly_order))
envelope_values = envelope(range(spectra.shape[0]))

print "\n## Response Polynomial"
print envelope

plt.plot(range(spectra.shape[0]), envelope_values, 'k', linewidth=2, label="envelope")
plt.legend()
plt.title("Runs 19-27, FEE Spectrometer, summed up")
plt.show()
