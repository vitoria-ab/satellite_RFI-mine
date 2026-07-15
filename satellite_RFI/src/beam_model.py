"""
Defines functions to simulate MeerKAT's beam model; haven't rewritten most of these, since the most useful one (EMSS beam model) is in a specific ILIFU directory that I can't reach.

Functions
---------
_get_Khans(phi=None)
Khans_beam_model(freq=None, theta=None)
Cosine_beam_model(freq, dish_diameter=13.5)
emss_beam(freq, theta)
emss_beam_model(f)
khan_emss_beam(freqs, theta)
khan_emss_beam_model(f)

Classes
-------
unsorted_interp2d(interp2d): 
    __call__
"""


# -------------------------------------------------- #
## -------------------- IMPORTS ------------------- ##
# -------------------------------------------------- #

import numpy as np
from astropy.io import fits
from scipy.interpolate import interp1d, interp2d
from scipy.interpolate import RectBivariateSpline
import pickle


# -------------------------------------------------- #
## ------------------- FUNCTIONS ------------------ ##
# -------------------------------------------------- #

def EMSS_interpolator():
    ''' Gets the EMSS beam model data and creates an interpolator;
    to get the best performance, create this function once and pass
    it to the EMSS function. '''
    
    # getting data
    fname = "/idia/projects/hi_im/MeerKAT_beams/v4/MK_Lband_1D_Beam_data"
    with open(fname, "rb") as f:
        data = pickle.load(f, encoding="latin1")
    freq_beam = data["freq"]
    theta_beam = data["th"]
    
    # getting averaged and normalized polarization
    Pv = data["P_v_th"]
    Ph = data["P_h_th"]
    P = (Pv/Pv.max(axis=1,keepdims=True) + Ph/Ph.max(axis=1,keepdims=True)) / 2
    
    # creating interpolator in the (fxtheta) grid
    interp = RectBivariateSpline(freq_beam, theta_beam, P, kx=3, ky=3)
    return interp


# -------------------------------------------------- #

def EMSS(frequency, theta, _interp=None):
    ''' Calculates the EMSS beam model for MeerKAT interpolated
    in a (freq x theta) grid. 
    
    Parameters
    ----------
    frequency : ndarray
        List of frequencies (MHz).
    theta : ndarray or np.MaskedArray
        List of time instances (s).
    interp : func (default None)
        The interpolation function (retrieved from the data); if
        it was not called beforehand, EMSS_interpolator is used.
    
    Returns
    -------
    beam : ndarray or np.MaskedArray
        (freq x theta) matrix of the EMSS beam.
    '''
    # getting interpolator if necessary
    if _interp is None:  _interp = _EMSS_interpolator()

    # removing the mask (and later re-apply)
    is_masked = np.ma.isMaskedArray(theta)
    if is_masked:
        mask = theta.mask;  theta = theta.data

    # calculating funcion at the grid and re-applying mask
    Xs, Ys = np.meshgrid(frequency, theta, indexing="ij")
    beam = _interp(Xs.ravel(),Ys.ravel(),grid=False).reshape(Xs.shape)
    if is_masked:  
        beam = np.ma.array(beam, mask=np.broadcast_to(mask,beam.shape))
    return beam



def _get_Khans(phi=None):
    ''' Recover Khan's beam model from the file for a given 
    polarization (internal function).
    
    Parameters
    ----------
    phi : string or None
        Polarization; for None it averages the behavior on both 
        polarizations (options: None, "HH", or "VV").
    
    Returns
    -------
    beam_mean : 2-d array of floats
        The beam model averaged on the central cut.
    _freq : array of floats
        Frequency array, between 800 and 1720.
    _theta : array of floats
        Angle array, between -5 and 5.
    '''

    # getting beam model
    beam_path = "/idia/users/ycli/meerkat_beam/"
    beam_file = "primary_beam_mh_184channels_10deg_re.fits"
    beam_data = fits.getdata(beam_path+beam_file)

    # defining frequencies and angles
    _theta = np.linspace(-5, 5, 256, dtype="float32")
    _freq = np.arange(800, 1720, 5, dtype="float32")

    # getting relevant quantities
    mid_idx = beam_data.shape[-1] // 2
    HH = beam_data[:,0,0,:,:]
    VV = beam_data[:,1,1,:,:]

    # calculating for each polarization option
    if phi is None:
        beam_HH = (HH[:,:,mid_idx]**2 + VV[:,:,mid_idx]**2) / 2
        beam_VV = (HH[:,mid_idx,:]**2 + VV[:,mid_idx,:]**2) / 2
        beam_mean = (beam_HH+beam_VV) / 2
    elif phi=="HH":
        beam_mean = HH[:,:,mid_idx]**2
    elif phi=="VV":
        beam_mean = VV[:,mid_idx,:]**2
        
    beam_mean = beam_mean.astype("float32")
    return beam_mean, _freq, _theta


# -------------------------------------------------- #

def Khans_beam_model(freq=None, theta=None):
    ''' Returns Khan's beam model interpolated as a 2d or 1d function.
    
    Parameters
    ----------
    freq : array of floats (optional)
        If not None, frequency on which to interpolate.
    theta : array of floats (optional)
        If not None, angle on which to interpolate.

    Returns
    -------
    beam_func : array of 1d or 2d funcs
        Functions that computes the beam model as a function of frequency
        or angle or both.
    '''

    beam_mean, _freq, _theta = _get_Khans()
    beam_func = interp2d(_theta, _freq, beam_mean)
    kwargs = {"bounds_error": False, "fill_value": 0}

    if freq is not None:
        _beam_func = interp1d(_theta, beam_func(_theta, freq).astype("float32"), axis=1, **kwargs)
        return lambda x: _beam_func(x)
    elif theta is not None:
        _beam_func = interp1d(_freq, beam_func(theta, _freq).astype("float32"), axis=0, **kwargs)
        return lambda x: _beam_func(x)
    else:
        return beam_func


# -------------------------------------------------- #

def Cosine_beam_model(freq, dish_diameter=13.5):
    ''' Returns cosine beam model, for a given frequency (in MHz).
    
    Parameters
    ----------
    freq : array of floats
        Frequency range.
    dish_diameter : float (optional)
        Diameter of telescope dish in m (default is 13.5m for MEERKAT).

    Returns
    -------
    cos_beam : array of funcs
        Cosine beam models for an array of frequencies.
    '''

    # getting quantities in SI
    c = 299792458  # speed of light in m/s
    lamb = c / (freq*1.0e6)  # wavelength in m
    fwhm = 1.16 * np.degrees(lamb / dish_diameter)  # FWHM in degrees
    fwhm = fwhm[:, None, None]

    # calculating model
    A = 1.189
    B = 4
    def cos_beam(x):
        term1 = np.cos(A * np.pi * x[None,...] / fwhm)
        term2 = 1 - B * (A * x[None,...] / fwhm)**2
        return (term1/term2)**2
    
    return cos_beam


# -------------------------------------------------- #

class unsorted_interp2d(interp2d):
    """
    Class that allows for un-ordered/masked data to be given
    """

    def __call__(self, x, y, dx=0, dy=0):
        unsorted_idxs = np.argsort(np.argsort(x))
        return interp2d.__call__(self, x, y, dx=dx, dy=dy)[:, unsorted_idxs]


# -------------------------------------------------- #

def emss_beam(freq, theta):
    """
    Using the EMSS beam function, an interpolation that takes in:
    frequency - range 900-1670MHz
    theta - range 0-100
    """
    
    # collecting and reading in the data
    beam = pickle.load(open("/idia/projects/hi_im/MeerKAT_beams/v4/MK_Lband_1D_Beam_data", "rb"))
    f = beam["freq"]
    Pv = beam["P_v_th"]
    Ph = beam["P_h_th"]
    th = beam["th"]

    # getting interpolated function    
    P_centered = ( Pv/np.max(Pv,axis=1)[:,np.newaxis] + Ph/np.max(Ph,axis=1)[:,np.newaxis] ) / 2
    P_interp = unsorted_interp2d(th, f, P_centered, kind="cubic")
    ##---------------------------------------------------------------------##

    # Checking to see if thet is a masked array, then only the data is used
    if isinstance(theta, np.ma.core.MaskedArray):
        masked = "y"
        theta_mask = theta.mask
        theta = np.array(theta)

    else:
        theta = np.array(theta)
        masked = None

    # Shape checking
    f_shape = freq.shape
    th_shape = theta.shape

    # Loop through all different satellites within in the constellation.

    if theta.ndim == 1:
        interp = P_interp(theta, freq)
        if masked == "y":
            interp = np.ma.array(interp, mask=interp * theta_mask[np.newaxis, :])
    elif theta.ndim == 2:
        interp = np.array([P_interp(theta[:, i], freq).T for i in range(th_shape[1])]).T
        # Broadcasting the 2d mask across 3d axis
        if masked == "y":
            interp = np.ma.array(interp, mask=interp * theta_mask[np.newaxis, :, :])

    return interp


# -------------------------------------------------- #

def emss_beam_model(f):
    """Takes in frequency values and creates a function for lambda values"""
    return lambda th: emss_beam(freq=f, theta=th)


# -------------------------------------------------- #

def khan_emss_beam(freqs, theta):
    """
    Fucntion that combines the khan beam and emss beam together. Assumes symmetry for Khan's beam
    Works only for masked arrays
    """
    khan = Khans_beam_model(freq=freqs, theta=None)
    emss = emss_beam_model(f=freqs)

    if isinstance(theta, np.ma.core.MaskedArray):
        masked = "y"

        theta_d = theta.data
        theta_m = theta.mask

        k_angle = khan(theta_d)
        e_angle = 0.2 * emss(theta_d)

    else:
        masked = None
        k_angle = khan(theta)
        e_angle = 0.2 * emss(theta)

    khan_emss = np.where(k_angle == 0, e_angle, k_angle)
    if masked == "y":
        khan_emss = np.ma.array(khan_emss, mask=khan_emss * theta_m[np.newaxis, :, :])

    return khan_emss


# -------------------------------------------------- #

def khan_emss_beam_model(f):
    """Takes in the frequency values and and returns a function for theta values."""
    return lambda th: khan_emss_beam(freqs=f, theta=th)


# -------------------------------------------------- #