import numpy as np
from time import time
import sys
import h5py
import pydoc


def images_iterator(images, chunk_size=1, mask=None):
    i = 0
    if chunk_size >= images.shape[0]:
        chunk_size = images.shape[0]

    for i in range(0, images.shape[0], chunk_size):
        end_i = min(i + chunk_size, images.shape[0])
        if mask is not None:
            idx = np.arange(images.shape[0])[mask]
            dset = images[idx[i:end_i]]
        else:
            dset = images[i:end_i]
        for j in range(dset.shape[0]): 
            yield dset[j]


def rebin(a, *args):
    """
    rebin a numpy array
    """
    shape = a.shape
    lenShape = len(shape)
    #factor = np.asarray(shape) / np.asarray(args)
    #print factor
    evList = ['a.reshape('] + ['args[%d],factor[%d],' % (i, i) for i in range(lenShape)] + [')'] + ['.mean(%d)' % (i + 1) for i in range(lenShape)]
    return eval(''.join(evList))


def image_get_spectra(results, temp, image_in, axis=0, thr_hi=None, thr_low=None):
    """Returns a spectra (projection) over an axis of an image. This function is to be used within an AnalysisProcessor instance.
    
    Parameters
    ----------
    results : dict
        dictionary containing the results. This is provided by the AnalysisProcessor class
    temp : dict
        dictionary containing temporary variables. This is provided by the AnalysisProcessor class
    image_in : Numpy array
        the image. This is provided by the AnalysisProcessor class
    axis: int, optional
        the axis index over which the projection is taken. This is the same as array.sum(axis=axis). Default is 0
    thr_hi: float, optional
        Upper threshold to be applied to the image. Values higher than thr_hi will be put to 0. Default is None
    thr_low: float, optional
        Lower threshold to be applied to the image. Values lower than thr_low will be put to 0. Default is None
    
    Returns
    -------
    results, temp: dict
        Dictionaries containing results and temporary variables, to be used internally by AnalysisProcessor
    """
    if axis == 1:
        other_axis = 0
    else:
        other_axis = 1

    # static type casting, due to overflow possibility...
    if temp["current_entry"] == 0:
        if temp["image_dtype"].name.find('int') !=-1:
            results["spectra"] = np.empty((results['n_entries'], temp["image_shape"][other_axis]), dtype=np.int64) 
        elif temp["image_dtype"].name.find('float') !=-1:
            results["spectra"] = np.empty((results['n_entries'], temp["image_shape"][other_axis]), dtype=np.float64) 
        
    # if there is no image, return NaN
    if image_in is None:
        result = np.ones(temp["image_shape"][other_axis], dtype=temp["image_dtype"])
        result[:] = np.NAN
    else:
        image = image_in.copy()
        if thr_low is not None:
            image[ image < thr_low] = 0
        if thr_hi is not None:
            image[ image > thr_hi] = 0
    
        result = np.nansum(image, axis=axis)

    #if result[result > 1000] != []:
    #    print temp['current_entry'], result[result > 1000]
    results["spectra"][temp['current_entry']] = result
    temp["current_entry"] += 1
    return results, temp

    
def image_get_mean_std(results, temp, image_in, thr_hi=None, thr_low=None):
    """Returns the average of images and their standard deviation. This function is to be used within an AnalysisProcessor instance.
    
    Parameters
    ----------
    results : dict
        dictionary containing the results. This is provided by the AnalysisProcessor class
    temp : dict
        dictionary containing temporary variables. This is provided by the AnalysisProcessor class
    image_in : Numpy array
        the image. This is provided by the AnalysisProcessor class
    thr_hi: float, optional
        Upper threshold to be applied to the image. Values higher than thr_hi will be put to 0. Default is None
    thr_low: float, optional
        Lower threshold to be applied to the image. Values lower than thr_low will be put to 0. Default is None
    
    Returns
    -------
    results, temp: dict
        Dictionaries containing results and temporary variables, to be used internally by AnalysisProcessor
    """
    if image_in is None:
        return results, temp
        
    image = image_in.copy()
    
    if thr_low is not None:
        image[ image < thr_low] = 0
    if thr_hi is not None:
        image[ image > thr_hi] = 0
    
    if temp["current_entry"] == 0:
        temp["sum"] = np.array(image)
        temp["sum2"] = np.array(image * image)
    else:
        temp["sum"] += image
        temp["sum2"] += np.array(image * image)

    temp["current_entry"] += 1    

    return results, temp    
    

def image_get_mean_std_results(results, temp):
    """Function to be applied to results of image_get_std_results. This function is to be used within an AnalysisProcessor instance, and it is called automatically.
    
    Parameters
    ----------
    results : dict
        dictionary containing the results. This is provided by the AnalysisProcessor class
    temp : dict
        dictionary containing temporary variables. This is provided by the AnalysisProcessor class
    
    Returns
    -------
    results: dict
        Dictionaries containing results and temporary variables, to be used internally by AnalysisProcessor. Result keys are 'images_mean' and 'images_std', which are the average and the standard deviation, respectively.
    """
    if not temp.has_key("sum"):
        return results        

    mean = temp["sum"] / temp["current_entry"]
    std = (temp["sum2"] / temp["current_entry"]) - mean * mean
    std = np.sqrt(std)
    results["images_mean"] = mean
    results["images_std"] = std
    return results


def image_get_histo_adu(results, temp, image, bins=None):
    """Returns the total histogram of counts of images. This function is to be used within an AnalysisProcessor instance. This function can be expensive.
    
    Parameters
    ----------
    results: dict
        dictionary containing the results. This is provided by the AnalysisProcessor class
    temp: dict
        dictionary containing temporary variables. This is provided by the AnalysisProcessor class
    image: Numpy array
        the image. This is provided by the AnalysisProcessor class
    bins: array, optional
        array with bin extremes        
        
    Returns
    -------
    results, temp: dict
        Dictionaries containing results and temporary variables, to be used internally by AnalysisProcessor
    """
    if image is None:
        return results, temp

    if bins is None:
        bins = np.arange(-100, 1000, 5)
    t_histo = np.bincount(np.digitize(image.flatten(), bins[1:-1]), 
                          minlength=len(bins) - 1)
    
    if temp["current_entry"] == 0:
        results["histo_adu"] = t_histo
        results["histo_adu_bins"] = bins
    else:
        results["histo_adu"] += t_histo

    temp["current_entry"] += 1
    return results, temp                  
  

def image_set_roi(image, roi=None):
    """Returns a copy of the original image, selected by the ROI region specified

    Parameters
    ----------
    image: Numpy array
        the input array image
    roi: array
        the ROI selection, as [[X_lo, X_hi], [Y_lo, Y_hi]]
        
    Returns
    -------
    image: Numpy array
        a copy of the original image, with ROI applied
    """
    if roi is not None:
        new_image = image[roi[0][0]:roi[0][1], roi[1][0]:roi[1][1]]
        return new_image
    else:
        return image
 
 
def image_set_thr(image, thr_low=None, thr_hi=None, replacement_value=0):
    """Returns a copy of the original image, with a low and an high thresholds applied

    Parameters
    ----------
    image: Numpy array
        the input array image
    thr_low: int, float
        the lower threshold
    thr_hi: int, float
        the higher threshold
    replacement_value: int, float
        the value with which values lower or higher than thresholds should be put equal to
        
    Returns
    -------
    image: Numpy array
        a copy of the original image, with ROI applied
    """
    new_image = image.copy()
    if thr_low is not None:
        new_image[new_image < thr_low] = replacement_value
    if thr_hi is not None:
        new_image[new_image > thr_hi] = replacement_value
    return new_image


def image_subtract_image(image, sub_image):
    """Returns a copy of the original image, after subtraction of a user-provided image (e.g. dark background)

    Parameters
    ----------
    image: Numpy array
        the input array image
    image: Numpy array
        the image to be subtracted

    Returns
    -------
    image: Numpy array
        a copy of the original image, with subtraction applied
    """
    new_image = image.copy()
    return new_image - sub_image


class Analysis(object):
    """Simple container for the analysis functions to be loaded into AnalysisProcessor. At the moment, it is only used internally inside AnalysisProcessor
    """
    def __init__(self, analysis_function, arguments={}, post_analysis_function=None, name=None):
        """
        Parameters
        ----------
        analysis_function: callable function
            the main analysis function to be run on images
        arguments: dict
            arguments to analysis_function
        post_analysis_function: callable function
            function to be called only once after the analysis loop
        """

        self.function = analysis_function
        self.post_analysis_function = post_analysis_function
        self.arguments = arguments
        if name is not None:
            self.name = name
        else:
            self.name = self.function.__name__
        self.temp_arguments = {}
        self.results = {}


class AnalysisProcessor(object):
    """Simple class to perform analysis on SACLA datafiles. Due to the peculiar file 
    format in use at SACLA (each image is a single dataset), any kind of
    analysis must be performed as a loop over all images: due to this, I/O is
    not optimized, and many useful NumPy methods cannot be easily used.
    
    With this class, each image is read in memory only once, and then passed 
    to the registered methods to be analyzed. All registered functions must:
    + take as arguments at least results (dict), temp (dict), image (2D array)
    + return results, temp
    
    `results` is used to store the results produced by the function, while
    `temp` stores temporary values that must be preserved during the image loop.
    
    A simple example is:

    def get_spectra(results, temp, image, axis=0, ):
        result = image.sum(axis=axis)
        if temp["current_entry"] == 0:
            results["spectra"] = np.empty((results['n_entries'], ) + result.shape, dtype=result.dtype) 
            
        results["spectra"][temp['current_entry']] = result
        temp["current_entry"] += 1
        return results, temp
    
    In order to apply this function to all images, you need to:
    
    # create an AnalysisOnImages object
    an = ImagesProcessor()

    # load a dataset from a SACLA data file
    fname = "/home/sala/Work/Data/Sacla/ZnO/257325.h5"
    dataset_name = "detector_2d_1"
    an.set_sacla_dataset(hf, dataset_name)

    # register the function:    
    an.add_analysis(get_spectra, args={'axis': 1})

    # run the loop
    results = an.analyze_images(fname, n=1000)

    """

    def __init__(self):
        self.results = []
        self.temp = {}
        self.functions = {}
        self.datasets = []
        self.f_for_all_images = {}
        self.analyses = []
        self.available_analyses = {}
        self.available_analyses["image_get_histo_adu"] = (image_get_histo_adu, None)
        self.available_analyses["image_get_mean_std"] = (image_get_mean_std, image_get_mean_std_results)
        self.available_analyses["image_get_spectra"] = (image_get_spectra, None)
        self.available_preprocess = {}
        self.available_preprocess["image_set_roi"] = image_set_roi
        self.available_preprocess["image_set_thr"] = image_set_thr
        self.n = -1
        self.flatten_results = False
        self.preprocess_list = []
        self.dataset_name = None

    def __call__(self, dataset_file, n=-1, tags=None ):
        return self.analyze_images(dataset_file, n=n, tags=tags)

    def add_preprocess(self, f, label="", args={}):
        """
        Register a function to be applied to all images, before analysis (e.g. dark subtraction)
        """
        if label != "":
            f_name = label
        elif isinstance(f, str):
            f_name = f
        else:
            f_name = f.__name__

        if isinstance(f, str):
            if not self.available_preprocess.has_key(f):
                raise RuntimeError("Preprocess function %s not available, please check your code" % f)
            self.f_for_all_images[f_name] = {'f': self.available_preprocess[f], "args": args}
        else:
            self.f_for_all_images[f_name] = {'f': f, "args": args}
        self.preprocess_list.append(f_name)
        
    def list_preprocess(self):
        """List all loaded preprocess functions
        
        Returns
        ----------
        list :
            list of all loaded preprocess functions
        """
        return self.preprocess_list
    
    def remove_preprocess(self, label=None):
        """Remove loaded preprocess functions. If called without arguments, it removes all functions.
        
        Parameters
        ----------
        label : string
            label of the preprocess function to be removed
        """
        if label is None:
            self.f_for_all_images = {}
            self.preprocess_list = []
        else:
            del self.f_for_all_images[label]
            self.preprocess_list.remove[label] 
    
    def add_analysis(self, f, result_f=None, args={}, label=""):
        """Register a function to be run on images
        
        Parameters
        ----------
        f: callable function
            analysis function to be loaded. Must take at least results (dict), temp (dict) and image (numpy array) as input, and return just results and temp. See main class help.
        result_f: callable function
            function to be applied to the results, at the end of the loop on images.
        args: dict
            arguments for the analysis function
        label : string
            label to be assigned to analysis function
            
        Returns
        -------
            None        
        """
        
        if isinstance(f, str):
            if not self.available_analyses.has_key(f):
                raise RuntimeError("Analysis %s not available, please check your code" % f)
            analysis = Analysis(self.available_analyses[f][0], arguments=args, 
                                post_analysis_function=self.available_analyses[f][1], name=f)
        else:
            if label != "":
                analysis = Analysis(f, arguments=args, post_analysis_function=result_f, name=label)
            else:
                analysis = Analysis(f, arguments=args, post_analysis_function=result_f)
        if analysis.name in self.list_analysis():
            print "[INFO] substituting analysis %s" % analysis.name
            self.remove_analysis(label=analysis.name)
        self.analyses.append(analysis)
        #return analysis.results

    def list_analysis(self):
        """List all loaded analysis functions
        
        Returns
        ----------
        list :
            list of all loaded analysis functions
        """
        return [x.name for x in self.analyses]

    def remove_analysis(self, label=None):
        """Remove a labelled analysis. If no label is provided, all the analyses are removed
        
        Parameters
        ----------
        label : string
            Label of the analysis to be removed        
        """
        
        if label is None:
            self.analyses = []
        else:
            for an in self.analyses:
                if an.name == label:
                    self.analyses.remove(an)

    #???
    def set_dataset(self, dataset_name, remove_preprocess=True):
        """Set the name for the SACLA dataset to be analyzed        
        Parameters
        ----------
        dataset_name : string
            Name of the dataset to be added, without the trailing `/run_XXXXX/`
        remove_preprocess : bool
            Remove all the preprocess functions when setting a dataset
        """
        self.dataset_name = dataset_name
        self.results = {}
        self.temp = {}
        if remove_preprocess:
            print "[INFO] Setting a new dataset, removing stored preprocess functions. To overcome this, use remove_preprocess=False"
            self.remove_preprocess()
        
    def analyze_images(self, fname, n=-1, tags=None):
        """Executes a loop, where the registered functions are applied to all the images
        
        Parameters
        ----------
        fname : string
            Name of HDF5 Sacla file to analyze
        n : int
            Number of events to be analyzed. If -1, then all events will be analyzed.
        tags : int list
            List of tags to be analyzed.
            
        Returns
        -------
        results: dict
            dictionary containing the results.
        """
        results = {}

        if tags == []:
            print "WARNING: emtpy tags list, returning nothing..."
            return results

        hf = h5py.File(fname, "r")

        self.run = hf.keys()[-1]  # find a better way
        if self.dataset_name is None:
            hf.close()
            raise RuntimeError("Please provide a dataset name using the `set_sacla_dataset` method!")

        self.datasetname_main = "/Configure:0000/Run:0000/CalibCycle:0000/"     
        main_dataset = hf[self.datasetname_main + self.dataset_name]
        dataset = main_dataset["image"]
        tags_list = 1e6 * main_dataset["time"]["seconds"].astype(long) + main_dataset["time"]["fiducials"]
        
        tags_mask = None
        dataset_indexes = np.arange(dataset.shape[0])
        if tags is not None:
            tags_mask = np.in1d(tags, tags_list, assume_unique=True)
            tags_list = dataset_indexes[tags_mask]
            
        n_images = len(tags_list)
        if n != -1:
            if n < len(tags_list):
                n_images = n
                
        for analysis in self.analyses:
            analysis.results = {}
            analysis.results["n_entries"] = n_images
            analysis.results["filename"] = fname
            analysis.temp_arguments = {}
            analysis.temp_arguments["current_entry"] = 0
            analysis.temp_arguments["image_shape"] = None
            analysis.temp_arguments["image_dtype"] = None

            # here do the bunch load on tags_list
            chunk_size = 100
            analysis.temp_arguments["image_shape"] = dataset[0].shape
            analysis.temp_arguments["image_dtype"] = dataset[0].dtype
        # loop on tags
        images_iter = images_iterator(dataset, chunk_size, tags_mask)
        for image_i, image in enumerate(images_iter):
            if image_i >= n_images:
                break
            
            if self.f_for_all_images != {}:
                 for k in self.preprocess_list:
                     image = self.f_for_all_images[k]['f'](image, **self.f_for_all_images[k]['args'])

            if image is not None and analysis.temp_arguments["image_shape"] is not None:
                analysis.temp_arguments["image_shape"] = image.shape
                analysis.temp_arguments["image_dtype"] = image.dtype

            for analysis in self.analyses:
                analysis.results, analysis.temporary_arguments = analysis.function(analysis.results, analysis.temp_arguments, image, **analysis.arguments)
            
        for analysis in self.analyses:
            if analysis.post_analysis_function is not None:
                analysis.results = analysis.post_analysis_function(analysis.results, analysis.temp_arguments)
            if self.flatten_results:
                results.update(analysis.results)
            else:
                results[analysis.name] = analysis.results
        self.results = results
        hf.close()
        return self.results

    def print_help(self, label=""):
        """Print help for a specific analysis or preprocess function
        
        Parameters
        ----------
        label : string
            Label of the analysis or preprocess function whose help should be printed        
        """
        if label is "":
            print """\n
            ######################## 
            # Preprocess functions #
            ########################\n"""
            for f in self.available_preprocess.values():
                print pydoc.plain(pydoc.render_doc(f))

            print """\n
            ######################## 
            # Analysis  functions  #
            ########################\n"""
            for f in self.available_analyses.values():
                print pydoc.plain(pydoc.render_doc(f[0]))
        else:
            if self.available_preprocess.has_key(label):
                print """\n
                ######################## 
                # Preprocess functions #
                ########################\n"""
                print pydoc.plain(pydoc.render_doc(self.available_preprocess[label]))
            elif self.available_analyses.has_key(label):
                print """\n
                ######################## 
                # Analysis  functions  #
                ########################\n"""
                print pydoc.plain(pydoc.render_doc(self.available_analyses[label][0]))
            else:
                print "Function %s does not exist" % label
                
        
