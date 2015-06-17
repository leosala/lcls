# -*- coding: utf-8 -*-
"""
Created on Wed May 20 14:45:14 2015

@author: sala
"""

import h5py
import matplotlib.pyplot as plt
import numpy as np
from numba import jit, autojit, njit, double, int32
from time import time
import pandas as pd



    #fname = "/media/sala/Elements/Data/SwissFEL/TestData/XPP/FEE_Spectrometer/xppc0114-r0270.h5"
    
#f = h5py.File(fname, "r")
#f_old = h5py.File("/media/sala/Elements/Data/LCLS/CXI/cxi61812-r0196.h5", "r")
   
main_dsetname = "/Configure:0000/Run:0000/CalibCycle:0000/"
#main_dset = f[main_dsetname]    
# Name of OPAL and FEE datasets
opal_name = "Camera::FrameV1/XppEndstation.0:Opal1000.0"
fee_name = "Camera::FrameV1/XrayTransportDiagnostic.0:Opal1000.0"
    
#fee_t = main_dset[fee_name]["time"]
#fee = main_dset[fee_name]["image"]
#print fee.dtype, fee.shape

#entries = fee.shape[0]



def dset_loop(dset, entries=99999):
    """Simple loop over an array"""
    shape = dset.shape
    sase_map = np.zeros((min(entries, shape[0]), dset[0].shape[0]))
    for i in range(min(entries, shape[0])):
        sase_map[i] = dset[i].sum(axis=1)
    
    return sase_map


def dset_loop_2(dset, res, entries=99999):
    """Simple loop over an array"""
    shape = dset.shape
    #sase_map = np.zeros((min(entries, shape[0]), dset[0].shape[0]))
    for i in range(min(entries, shape[0])):
        res[i] = dset[i].sum(axis=1)
    
    return res


def dset_loop_chunk(dset, entries, chunk_size=100):
    """Apply numpy ufunc over a chunk of an array"""
    shape = dset.shape
    sase_map = np.zeros((min(entries, shape[0]), dset[0].shape[0]))
    for i in range(0, min(entries, shape[0]), chunk_size):
        end_i = min(i + chunk_size, shape[0])
        sase_map[i:end_i] = dset[i:end_i].sum(axis=2)
    
    return sase_map


def dset_loop_chunk_loop(dset, entries, chunk_size=100):
    """Perform the loop over an array chunk"""
    shape = dset.shape
    sase_map = np.zeros((min(entries, shape[0]), dset[0].shape[0]))
    for i in range(0, min(entries, shape[0]), chunk_size):
        end_i = min(i + chunk_size, shape[0])
        sase_map[i:end_i] = dset_loop(dset[i:end_i])
    
    return sase_map


def dset_loop_chunk_numba(dset, entries, chunk_size=100):
    """Apply an autojit loop function on an array chunk"""
    shape = dset.shape
    sase_map = np.zeros((min(entries, shape[0]), dset[0].shape[0]))
    images_loop = jit(dset_loop)
   
    for i in range(0, min(entries, shape[0]), chunk_size):
        end_i = min(i + chunk_size, shape[0])
        #res = np.zeros((end_i - i, dset[0].shape[0]))
        sase_map[i:end_i] = images_loop(dset[i:end_i], 999999)
    
    return sase_map


   
    
# does not work
#def generate_custom_function(func, f_args={}): 
#    '''Return a custom compiled function that calls `func`.''' 
#    def eval_fun(a, f_args): 
#        return func(a, **f_args) 
#
#    return autojit(eval_fun) 
#def dset_apply_f(dset, entries, f, f_args={}, chunk_size=100):
#    shape = dset.shape
#    sase_map = np.zeros((min(entries, shape[0]), dset[0].shape[0]))
#    #images_loop = autojit(dset_loop_f)
#    images_loop = generate_custom_function(np.sum, {}) 
#    print images_loop([], )
#    #res = eval_fun(0.5) 
#    #for i in range(0, min(entries, shape[0]), chunk_size):
#    #    end_i = min(i + chunk_size, shape[0])
#    #    sase_map[i:end_i] = dset_loop_f(dset[i:end_i], f=images_loop, f_args=f_args)
#    
#    return sase_map
#def dset_loop_f(dset, f, f_args={}, entries=99999):
#    shape = dset.shape
#    sase_map = np.zeros((min(entries, shape[0]), dset[0].shape[0]))
#    for i in range(min(entries, shape[0])):
#        sase_map[i] = f()  #dset[i], f_args)
#    
#    return sase_map
# 

def test(test_n=0):
    entries=100
    if entries == -1 or entries > fee.shape[0]:
        entries = fee.shape[0]

    res_tmp = {}
    #res_tmp["entries"] = [entries]
    
    if test_n==0:
        start_t = time()
        sase_map = dset_loop_chunk(fee, entries)
        print "Numpy chunked loop: %s" % (time() - start_t)
        res_tmp["np chunk"] = [time() - start_t,]
    
    elif test_n==1:   
        start_t = time()
        sase_map = dset_loop_chunk_loop(fee, entries)
        print "Numpy chunked loop loop: %s" % (time() - start_t)
        res_tmp["np chunk loop"] = [time() - start_t,]
    
    elif test_n==2:    
        start_t = time()
        sase_map = dset_loop_chunk_numba(fee, entries)
        print "Numba chunked loop: %s" % (time() - start_t)
        res_tmp["numba chunk"] = [time() - start_t,]

    # very slow!
    #if fee[0].shape[0] < 2000:
    elif test_n==3:
        
        dset_loop_numba = autojit(dset_loop)
        start_t = time()
        sase_map = dset_loop_numba(fee, entries)
        print "Numba loop: %s" % (time() - start_t)
        res_tmp["numba loop"] = [time() - start_t]
    
        # very slow!
    elif test_n==4:
        start_t = time()
        sase_map = dset_loop(fee, entries)
        print "Python loop: %s" % (time() - start_t)
        res_tmp["python loop"] = [time() - start_t]

    elif test_n==5:
        try:
            start_t = time()
            sase_map = fee[:entries].sum(axis=2)
            print "Numpy: %s" % (time() - start_t)
            res_tmp["np"] = [time() - start_t,]
        except:
            res_tmp["np"] = [np.nan]
    #except:
    #    pass

    return res_tmp


if __name__ == "__main__":
   
    main_dsetname = "/Configure:0000/Run:0000/CalibCycle:0000/"
    # Name of OPAL and FEE datasets
    #opal_name = "Camera::FrameV1/XppEndstation.0:Opal1000.0"
    fee_name = "Camera::FrameV1/XrayTransportDiagnostic.0:Opal1000.0"
    #fname = "/home/sala/Work/Data/SwissFEL/TestData/XPP/FEE_Spectrometer/xppc0114-r0270.h5"
    results = {}
    for it in range(2):
        for run in range(6):
            for events in [100, 200, 300, 400, 500, 750, 1000, 1500]:
                #fname = "/home/sala/Work/Data/gauss_%dx%d.h5" % (events, events)
                fname = "/home/sala/Work/Data/gauss_%dx%d_chunk1img_shuffle_gzip1.h5" % (events, events)
                #fname = "/home/sala/Work/Data/gauss_%dx%d.h5" % (events, events)
                #print fname
                f = h5py.File(fname, "r")
                #main_dset = f[main_dsetname]    
                #fee_t = main_dset[fee_name]["time"]
                #fee = f[main_dsetname + fee_name]["image"]
                fee = f["mydata"]
                print
                print "### n events:", it, run, events
                print fee.dtype, fee.shape
                tmp_res = test(run)
                print tmp_res
                for k, v in tmp_res.iteritems():
                    
                    if results.has_key(k):
                        results[k].append(v[0])
                        if run == 0:
                            results["pixels"].append(events)
                    else:
                        results[k] = v
                        if run == 0:
                            results["pixels"] = [events]
                    
                
                f.close()
    df = pd.DataFrame(results)
    df.to_csv("meas_gauss_%dx%d_chunk1img_shuffle_gzip1.txt" % (events, events), sep="\t") 
    df = df.set_index("pixels")
    #df.plot(marker="o")

#plt.figure()
#plt.imshow(sase_map)3
#plt.colorbar()