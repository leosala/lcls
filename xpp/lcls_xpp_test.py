# -*- coding: utf-8 -*-
"""
Created on Fri May 15 20:06:19 2015

@author: sala
"""

import numpy as np
import h5py
import matplotlib.pyplot as plt
import hdf5_utilities as h5u
import xpp_utils as xpp


def lcls_xpp_test(do_plot=False):
    fname = "/home/sala/Work/Data/SwissFEL/TestData/XPP/FEE_Spectrometer/xppc0114-r0270.h5"
    #fname = "/media/sala/Elements/Data/SwissFEL/TestData/XPP/FEE_Spectrometer/xppc0114-r0270.h5"
    
    f = h5py.File(fname, "r")
    f_old = h5py.File("/media/sala/Elements/Data/LCLS/CXI/cxi61812-r0196.h5", "r")
    
    main_dsetname = "/Configure:0000/Run:0000/CalibCycle:0000/"
    main_dset = f[main_dsetname]
    
    # Gas detectors. In older code, the average of 11,12,21,22 was taken as  getPhotonPulseEnergy
    print main_dset.keys()
    #gas = main_dset['Bld::BldDataFEEGasDetEnergyV1/FEEGasDetEnergy']["data"]
    #gas_t = main_dset['Bld::BldDataFEEGasDetEnergyV1/FEEGasDetEnergy']["time"]
    
    df = xpp.get_data(fname, ["fee_gas_det", "beam_energy"])
    
    if do_plot:
        gas_dets = ['f_11_ENRC', 'f_12_ENRC', 'f_21_ENRC', 'f_22_ENRC', 'f_63_ENRC', 'f_64_ENRC']
        plt.figure()
        for i, t in enumerate(gas_dets):
            plt.subplot(3, 2, i + 1)
            plt.title(t)
            df["fee_gas_det." + t].hist(bins=20)
            #plt.hist(gas[t], bins=20)
        plt.tight_layout()
        plt.show()
    
    
    # Beam energy
    print main_dset.keys()
    ebeam_dset = h5u.search_hdf5(main_dset, "EBeam/data", ).keys()[0].replace("data", "")
    ebeam = main_dset[ebeam_dset]['data']
    ebeam_t = main_dset[ebeam_dset]['time']
    
    # from old code
    photon_energy = 0.0444444 * np.power(ebeam['fEbeamL3Energy'], 2)*1.e-6
    # from XPP code: calcEBeam.m
    photon_energy = 44.42 * np.power((0.001 * ebeam['fEbeamL3Energy'] - 
        0.001 * 0.0016293 * ebeam['fEbeamPkCurrBC2'] -
        0.0005 * (0.63 * 0.001 * ebeam['fEbeamL3Energy'] + 
        0.0003 * ebeam['fEbeamPkCurrBC2'])), 2)
    
    
    # Get the present peak current in Amps
    beam_peak_current = ebeam["fEbeamPkCurrBC2"];
    
    # Get present beam energy [GeV]?
    #DL2energyGeV = 0.001*EBeam.fEbeamL3Energy;
    
    #%// wakeloss prior to undulators
    #LTUwakeLoss = 0.0016293*peakCurrent;
    #
    #%// Spontaneous radiation loss per segment
    #SRlossPerSegment = 0.63*DL2energyGeV;
    
    #%// wakeloss in an undulator segment
    #wakeLossPerSegment = 0.0003*peakCurrent;
    #
    #%// energy loss per segment
    #energyLossPerSegment = SRlossPerSegment + wakeLossPerSegment;
    
    #%// energy in first active undulator segment [GeV]
    #energyProfile = DL2energyGeV - 0.001*LTUwakeLoss - 0.0005*energyLossPerSegment;
    #
    #%// Calculate the resonant photon energy of the first active segment
    #photonEnergyeV = 44.42*energyProfile.*energyProfile;
    
    # getEBeamXPositionAtLTU(self,eventNumber): # Linac-To-Undulator; in mm, fEbeamLTUPosX
    # getEBeamXAngleAtLTU(self,eventNumber): # in mrad
    
    
    # Controls pv values (I assume... always found it empty)
    #print f_old[main_dsetname + '/ControlData::ConfigV3/'].keys()
    
    # EPICS channels. Each dataset is composed by data and time
    epics_channels = f[main_dsetname + "/Epics::EpicsPv/EpicsArch.0:NoDevice.0/"]
    #dtype=[('pvId', '<i2'), ('dbrType', '<i2'), ('numElements', '<i2'), ('status', '<i2'), ('severity', '<i2'), ('stamp', [('secPastEpoch', '<u4'), ('nsec', '<u4')]), ('value', '<f8')])
    
    
    # BPMs: any dataset with /XppMonPim ?
    
    # IPM? 
    #u'Configure:0000/Run:0000/CalibCycle:0000/Ipimb::DataV2/XppEnds_Ipm0/data
    
    # Main dataset for FEE / OPAL cameras
    dset_c = 'Configure:0000/Run:0000/CalibCycle:0000/Camera::FrameV1'
    
    # Name of OPAL and FEE datasets
    opal_name = "/XppEndstation.0:Opal1000.0"
    fee_name = "/XrayTransportDiagnostic.0:Opal1000.0"
    
    fee_t = f[dset_c + fee_name]["time"]
    fee = f[dset_c + fee_name]["image"]
    print fee.dtype, fee.shape
    # tags - vector or fiducials?
    #plt.plot(ebeam_t['vector'])
    #plt.plot(gas_t['vector'])
    #plt.plot(fee_t['vector'])
    #plt.show()
    
    #common_tags = np.intersect1d(ebeam_t['fiducials'], fee_t['fiducials'])
    
    import pandas as pd
    
    print ebeam_t["fiducials"][0:20]
    print fee_t["fiducials"][0:20]
    
    fee_sum = fee[:].sum(axis=1).sum(axis=1)
    df = pd.DataFrame({"tags": ebeam_t["fiducials"], "photon_energy": photon_energy}, ).set_index("tags")
    df2 = pd.DataFrame({"tags": fee_t["fiducials"], "FEE_sum": fee_sum}).set_index("tags")
    df = pd.concat([df, df2], axis=1)

    if do_plot:
        df.plot(kind="scatter", x="photon_energy", y="FEE_sum")
       
        plt.imshow(fee[:].sum(axis=2))
        plt.show()
        
        plt.plot(fee[0].sum(axis=1))
        plt.plot(fee[1].sum(axis=1))
        plt.plot(fee[2].sum(axis=1))
        plt.show()
    
if __name__ == "__main__":
    lcls_xpp_test(do_plot=True)