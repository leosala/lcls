# -*- coding: utf-8 -*-
"""
Created on Tue May 26 16:16:34 2015

@author: sala
"""

from images_processor import ImagesProcessor
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt


def plot_image_and_proj(image, title=""):
    plt.figure()
    gs = gridspec.GridSpec(3, 2, width_ratios=[3, 1], height_ratios=[0.2, 3, 1]) 
    ax0 = plt.subplot(gs[1,0])
    plt.title(title)
    ims = plt.imshow(image, aspect="auto")
    
    ax2 = plt.subplot(gs[2,0], sharex=ax0, )
    plt.plot(image.sum(axis=0))
    plt.subplot(gs[1,1], sharey=ax0)
    plt.plot(image.sum(axis=1), range(len(image.sum(axis=1))))

    ax = plt.subplot(gs[0,0])
    plt.colorbar(ims, orientation="horizontal", cax=ax)
    
    plt.tight_layout()


DIR = "/home/sala/Work/Data/LCLS/"
#fname = DIR + "cxi61812-r0196.h5"
fname = DIR + "/LH60/xpph6015-r0002.h5"
dset_main = "/Configure:0000/Run:0000/CalibCycle:0000/"
dset_name = "CsPad2x2::ElementV1/XppGon.0:Cspad2x2.0"
#dset_name = "CsPad2x2::ElementV1/CxiSc2.0:Cspad2x2.0"

ip = ImagesProcessor()
ip.set_dataset(dset_main + dset_name)
ip.add_analysis('image_get_mean_std')
ip.add_analysis('image_get_histo_adu')

ip.set_images_iterator('images_iterator_cspad140')
results = ip.analyze_images(fname, )

images_mean = results["image_get_mean_std"]["images_mean"]
h = results["image_get_histo_adu"]

plot_image_and_proj(images_mean, title="CsPad #0")

plt.figure()
plt.title("CsPad 140 #0")
plt.bar(h["histo_adu_bins"][:-1], h["histo_adu"], width=5, log=True)


dset_name = "CsPad2x2::ElementV1/XppGon.0:Cspad2x2.1"
ip.set_dataset(dset_main + dset_name)
results = ip.analyze_images(fname, )

images_mean = results["image_get_mean_std"]["images_mean"]
h = results["image_get_histo_adu"]
plot_image_and_proj(images_mean, title="CsPad #1")
plt.figure()
plt.title("CsPad 140 #0")
plt.bar(h["histo_adu_bins"][:-1], h["histo_adu"], width=5, log=True)


#FEE

opal_0 = dset_main + "/Camera::FrameV1/XppEndstation.0:Opal1000.0"
opal_1 = dset_main + "/Camera::FrameV1/XppEndstation.0:Opal1000.1"

ip.set_dataset(opal_0)
ip.set_images_iterator('images_iterator')
results_opal = ip.analyze_images(fname, n=100)

images_mean = results_opal["image_get_mean_std"]["images_mean"]
h = results_opal["image_get_histo_adu"]

plt.figure()
plt.subplot(211)
plt.title("Opal0")
plt.imshow(images_mean, aspect="auto")
plt.colorbar()
plt.subplot(212)
plt.title("Opal0")
plt.plot(images_mean.sum(axis=0))
plt.plot(images_mean.sum(axis=1))

ip.set_dataset(opal_1)
ip.set_images_iterator('images_iterator')
results_opal = ip.analyze_images(fname, n=100)

images_mean = results_opal["image_get_mean_std"]["images_mean"]
h = results_opal["image_get_histo_adu"]

plt.figure()
plt.subplot(211)
plt.title("Opal1")
plt.imshow(images_mean, aspect="auto")
plt.colorbar()
plt.subplot(212)
plt.title("Opal1")
plt.plot(images_mean.sum(axis=0))
plt.plot(images_mean.sum(axis=1))
