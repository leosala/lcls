# -*- coding: utf-8 -*-
"""
Created on Tue May 19 14:36:10 2015

@author: sala
"""

from sys import exit
import numpy as np
import pandas as pd
import h5py

import hdf5_utilities as h5u
reload(h5u)

quant_map = {}
quant_map["beam_energy"] = "Bld::BldDataEBeam"
quant_map["fee_gas_det"] = "FEEGasDetEnergy"


def compute_beam_energy(ebeam):
    beam_energy = 44.42 * np.power((0.001 * ebeam['fEbeamL3Energy'] - 
                  0.001 * 0.0016293 * ebeam['fEbeamPkCurrBC2'] -
                  0.0005 * (0.63 * 0.001 * ebeam['fEbeamL3Energy'] + 
                  0.0003 * ebeam['fEbeamPkCurrBC2'])), 2)

    return beam_energy

def get_data_with_tags(fname, quant, conf_cycle=0, run_cycle=0, calib_cycle=0):
    #for quant in quants:
    #    if not quant_map.has_key(quant):
    #        quant_map[quant] = quant
    f = h5py.File(fname, 'r')
    main_dsetname = "/Configure:%04d/Run:%04d/CalibCycle:%04d/" % (conf_cycle, run_cycle, calib_cycle)
    dset = f[main_dsetname + quant]
    tags = 1e6 * dset.parent['time']["seconds"].astype(long) + dset.parent['time']["fiducials"]
    return dset, tags


def get_scalar_data(fname, quants, conf_cycle=0, run_cycle=0, calib_cycle=0, ):
    if isinstance(quants, str):
        quants = [quants]
    for quant in quants:
        if not quant_map.has_key(quant):
            quant_map[quant] = quant
            print quant
            #print "[ERROR] Quantity '%s' not available" % quant
            #print "Available values are: ", quant_map.keys()
            #exit(-1)   
    
    f = h5py.File(fname, 'r')
    main_dsetname = "/Configure:%04d/Run:%04d/CalibCycle:%04d" % (conf_cycle, run_cycle, calib_cycle)
    main_dset = f[main_dsetname]
        
    if isinstance(quants, str):
        quants = [quants]
        
    for quant_i, quant in enumerate(quants):
        possible_datasets = h5u.search_hdf5(main_dset, quant_map[quant], print_datasets=False)
        # removing the last part of dataset name, as /time, /data, etc
        possible_datasets = set([x[:x.rfind("/")] for x in possible_datasets])
        if len(possible_datasets) == 0:
            print "[ERROR] No suitable dataset found for for %s, please check" % quant
            exit(-1)
        if len(possible_datasets) > 1:
            print "[ERROR] Too many selected datasets for %s, please check" % quant
            exit(-1)
        
        dset_name = possible_datasets.pop()
    
        dset_data = main_dset[dset_name + "/data"]
        dset_time = main_dset[dset_name + "/time"]    
    
        pd_dict = {}
        pd_dict["tags"] = 1000000 * dset_time["seconds"].astype(long) + dset_time["fiducials"]
        if quant_i == 0:
            pd_dict["time"] = dset_time["seconds"] + 1e-6 * dset_time["seconds"]
            pd_dict["fiducials"] = dset_time["fiducials"]
        if dset_data.dtype.fields == ():
            pd_dict[quant] = dset_data
        else:
            for field in dset_data.dtype.fields:
                if len(dset_data[field].shape) != 1:
                    print "[WARNING] Dataset %s cannot be loaded, as it is not a scalar dataset" % ("/".join((quant, field)))
                    continue
                pd_dict[quant + "." + field] = dset_data[field]
    
        # special cases
        if quant == "beam_energy":
            pd_dict[quant] = compute_beam_energy(dset_data)
    
        df = pd.DataFrame(pd_dict).set_index("tags")
        if quant_i == 0:
            df_total = df
        else:
            df_total = pd.concat([df_total, df], axis=1)
    f.close()
    return df_total
    
    
