import numpy as np
from astropy.io import fits
from scipy.interpolate import interp1d, interp2d
import pickle
# ----------------------------------------------------------------------------------------------------

def _Khans_beam_model(phi=None):

    beam_path = '/idia/users/ycli/meerkat_beam/'
    beam_file = 'primary_beam_mh_184channels_10deg_re.fits'

    with fits.open(beam_path + beam_file) as hdul:
        beam_data = hdul[0].data
        
    _theta = np.linspace(-5, 5, 256, dtype='float32')
    _freq  = np.arange(800, 1720, 5, dtype='float32')
    
    if phi is None:
        beam_profile = beam_data[:, 0, 0, ...] ** 2 + beam_data[:, 1, 1, ...] ** 2
        beam_profile /= 2.

        mid_idx = beam_profile.shape[1] / 2
        beam_HH = beam_profile[:, :, mid_idx]
        beam_VV = beam_profile[:, mid_idx, :]
        beam_mean = 0.5 * (beam_HH + beam_VV)
    elif phi == 'HH':
        beam_profile = beam_data[:, 0, 0, ...] ** 2
        mid_idx = beam_profile.shape[1] / 2
        beam_HH = beam_profile[:, :, mid_idx]
        #beam_HH = beam_profile[:, mid_idx, :]
        beam_mean = beam_HH
    elif phi == 'VV':
        beam_profile = beam_data[:, 1, 1, ...] ** 2
        mid_idx = beam_profile.shape[1] / 2
        beam_VV = beam_profile[:, mid_idx, :]
        beam_mean = beam_VV

    beam_mean = beam_mean.astype('float32')

    return beam_mean, _freq, _theta

    #if axis == 1:
    #    beam_intf  = interp1d(_theta, beam_mean, axis=1,bounds_error=False, fill_value=0)
    #    return beam_intf, _freq

    #elif axis == 0:
    #    beam_intf  = interp1d(_freq, beam_mean, axis=0,bounds_error=False, fill_value=0)
    #    return beam_intf, _theta

def Khans_beam_model(freq=None, theta=None):

    beam_mean, _freq, _theta = _Khans_beam_model()

    beam_func = interp2d(_theta, _freq, beam_mean)

    kwargs = { 'bounds_error' :False, 'fill_value': 0 }

    if freq is not None:
        _beam_func = interp1d(_theta, beam_func(_theta,  freq).astype('float32'), axis=1, **kwargs)
        return lambda x: _beam_func(x)
    elif theta is not None:
        _beam_func = interp1d(_freq,  beam_func(theta,  _freq).astype('float32'), axis=0, **kwargs)
        return lambda x: _beam_func(x)
    else:
        return beam_func






def get_OmegaA_from_Khans_beam(freq, threshold=0.):

    beamf, _freq = Khans_beam_model()
    d_theta = 0.01
    theta = np.arange(0, 5, d_theta)
    p = beamf(theta)
    p[p<threshold] = 0.
    theta *= np.pi / 180.
    d_theta *= np.pi / 180.
    omega_a = 2. * np.pi * np.sum(p * np.sin(theta)[None, :] * d_theta, axis=1)
    omega_a_f = interp1d(_freq, omega_a)

    return omega_a_f(freq)


def get_fwhm_from_Khans_beam(freq):

    beam, _t = Khans_beam_model(axis=0)
    _freq = np.arange(800, 1720, 10)
    width = lambda x, f: interp1d(beam(f)[128:], _t[128:])(x)
    _fwhm = []
    for _f in _freq:
        _fwhm.append(width(0.5, _f))
    _fwhm = np.array(_fwhm)
    
    return interp1d(_freq, _fwhm)(freq) * 2.

def get_factor_from_Khans_beam(freq, angle=0.5, phi=None):

    beam_intf, _freq = Khans_beam_model(phi=phi)
    
    factor = interp1d(_freq, beam_intf(angle))
    
    return factor(freq)


# ----------------------------------------------------------------------------------------------------

def Cosine_beam_model(freq):

    speed_of_light=299792458   # speed of light in m/s
    lamb=(speed_of_light/freq/1.0e6) # wavelength in m
    dish_diameter=13.5 # diameter of telescope dish in meters (m)
    fwhm=1.16*np.degrees(lamb/dish_diameter) # FWHM in degrees

    fwhm  = fwhm[:, None, None]

    A=1.189
    B=4
    return lambda x: (np.cos( A*np.pi*x[None, ...]/fwhm)/(1-B*(A*x[None, ...]/fwhm)**2))**2

# ----------------------------------------------------------------------------------------------------

class unsorted_interp2d(interp2d):
    '''
    Class that allows for un-ordered/masked data to be given
    '''
    def __call__(self, x, y, dx=0, dy=0):
        unsorted_idxs = np.argsort(np.argsort(x))
        return interp2d.__call__(self, x, y, dx=dx, dy=dy)[:, unsorted_idxs]

# ---------------------------------------------------------------------------------------------------- 
    
def emss_beam(freq, theta):
    '''
    Using the EMSS beam function, an interpolation that takes in:
    frequency - range 900-1670MHz
    theta - range 0-100
    '''
    ##--------------------------------------------------------------------##
    # Collecting and reading in the data
    beam = pickle.load(open('/idia/projects/hi_im/MeerKAT_beams/v4/MK_Lband_1D_Beam_data', 'rb'))

    f = beam['freq']
    Pv = beam['P_v_th'] 
    Ph = beam['P_h_th']
    th = beam['th']

    Pv_centered = np.array([Pv[i, :]/np.max(Pv[i, :]) for i in range(Pv.shape[0])])
    Ph_centered = np.array([Ph[i, :]/np.max(Ph[i, :]) for i in range(Ph.shape[0])])

    P_centered = (Pv_centered+Ph_centered)/2
    # Interpolatiion function
    P_interp = unsorted_interp2d(th, f, P_centered, kind='cubic')
    ##---------------------------------------------------------------------##
    
    # Checking to see if thet is a masked array, then only the data is used
    if isinstance(theta, np.ma.core.MaskedArray):
        masked = 'y'
        theta_mask = theta.mask
        theta = np.array(theta)
    
    else:
        theta = np.array(theta)
        masked = None
    
    # Shape checking
    f_shape = freq.shape
    th_shape = theta.shape

    # Loop through all different satellites within in the constellation. 
    
    if theta.ndim==1:
        interp = P_interp(theta, freq)
        if masked=='y':
            interp = np.ma.array(interp, mask=interp*theta_mask[np.newaxis,:])  
    elif theta.ndim==2:
        interp = np.array([P_interp(theta[:,i], freq).T for i in range(th_shape[1])]).T
        # Broadcasting the 2d mask across 3d axis
        if masked=='y':
            interp = np.ma.array(interp, mask=interp*theta_mask[np.newaxis,:,:])  

    return interp


def emss_beam_model(f):
    '''Takes in frequency values and creates a function for lambda values'''
    return lambda th : emss_beam(freq=f, theta=th)

# ----------------------------------------------------------------------------------------------------

def khan_emss_beam(freqs, theta):
    '''
    Fucntion that combines the khan beam and emss beam together. Assumes symmetry for Khan's beam
    Works only for masked arrays
    '''
    khan = Khans_beam_model(freq=freqs, theta=None)
    emss = emss_beam_model(f=freqs)
    
    if isinstance(theta, np.ma.core.MaskedArray):
        masked = 'y'
        
        theta_d = theta.data
        theta_m = theta.mask
    
        k_angle = khan(theta_d)
        e_angle = 0.2*emss(theta_d)
        
    else:
        masked=None
        k_angle = khan(theta)
        e_angle = 0.2*emss(theta)
        
    
    khan_emss = np.where(k_angle==0, e_angle, k_angle)
    if masked=='y':
        khan_emss = np.ma.array(khan_emss, mask=khan_emss*theta_m[np.newaxis,:,:])
    
    return khan_emss

def khan_emss_beam_model(f):
    '''Takes in the frequency values and and returns a function for theta values.'''
    return lambda th : khan_emss_beam(freqs=f, theta=th)

# ----------------------------------------------------------------------------------------------------
