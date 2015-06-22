# -*- coding: utf-8 -*-
"""
This script runs over a particular set of runs, used to calibrate the FEE spectrometer, and
then create a response function
"""
from __future__ import division

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
poly_order = 5

# x, y are the points we want to fit for the response envelope. Currently
# they are fitted with the max value
x = []
y = []

# eventual boundary conditions
x.append(0)
y.append(0)
x.append(2048)
y.append(0)

envelope = None

s_x = x
s_y = y

spectra_sum = None
plt.figure()
# running on all runs ranging from 19 till 26
for run in range(19, 27):
    fname = DIR + "xpph6015-r00%d.h5" % run
    print "Running on file %s" %fname
    # getting the data
    df = xpp.get_scalar_data(fname, dset_names["FeeGasDet"])
    # getting I0
    i0 = np.array(df["FEEGasDetEnergy.f_11_ENRC"].tolist())
    # IPM0 CH2 - need to use a different method, as it is composite data
    ipm0, ipm0_tags = xpp.get_data_with_tags(fname, dset_names["IPM0"])
    i0_ch2 = ipm0["channel"][:, 2]

    # Getting FEE spectra
    fee_spectra, fee_tags = xpp.get_data_with_tags(fname, dset_names["FEE_spectr_hproj"])
    # normalization
    spectra = fee_spectra[:].astype('int32').sum(axis=0) / i0_ch2.sum(axis=0)
    spectra_avg = np.max(spectra)
    spectra_std = spectra.std()
    if spectra_sum is None:
        spectra_sum = spectra.copy()
    else:
        spectra_sum += spectra

    s_t = np.where(np.isclose(spectra, spectra_avg, atol=500) == True)
    s_y.append(spectra_avg)
    idx = (np.abs(spectra - spectra_avg)).argmin()
    s_x.append(idx)
    print s_x, s_y
    # filling x, y
    y.append(spectra.max())
    t = np.where(spectra == y[-1])
    x.append(t[0][0])
    # plotting 
    plt.plot(spectra, label="Run %d" %run)

# creating the envelope
pol_fit, pol_cov = np.polyfit(x, y, poly_order, cov=True)
envelope = np.poly1d(pol_fit)
envelope_values = envelope(range(spectra.shape[0]))

plt.plot(range(spectra.shape[0]), envelope_values.max() * spectra_sum / spectra_sum.max(),  'k:', linewidth=2, label="normalized sum")
plt.plot(s_x, s_y, 'o', label="points for the fit")
print "\n## Response Polynomial"
print envelope
print "\n# Covariance Matrix"
print pol_cov

plt.plot(range(spectra.shape[0]), envelope_values, 'k', linewidth=2, label="envelope")
plt.legend()
plt.title("Runs 19-27, FEE Spectrometer spectra")
plt.show()
