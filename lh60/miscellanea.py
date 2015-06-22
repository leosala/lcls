"""
This file contains functions and definition which atm do not fit elsewhere
"""


#ImageProcessor preprocess function
def interpolate_pixel_hline(image, hpixel, axis=0, method="mean"):
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
        image[hpixel] = (image[hpixel - 1] + image[hpixel + 1]) / 2
    else:
        image[:, hpixel] = (image[:, hpixel - 1] + image[:, hpixel + 1]) / 2
    return image
