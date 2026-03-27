###################################################
# FILE: attenuation = attenuation_function(old)«
###################################################


## ----- IMPORTS ----- ##
import numpy as np


## ----- FUNCTIONS ----- ##
def tophat_oob(f, fi, band, level):
    """ Rectangular tophat function for out-of-band emission 
    (https://en.wikipedia.org/wiki/Rectangular_function). 

    Parameters
    ----------
    f : array of floats
        Frequency range.
    fi : float
        Central frequency of the band.
    band : float
        Half-width of the band.
    level : float
        Multiplying factor for the out-of-band emission.

    Returns
    -------
    final_values : array of floats
        Final values after applying the tophat attenuation.
    """

    mask = np.abs(f-fi) < band
    final_values = np.where(mask, 1, level)
    return final_values



def gaussian_oob(f, fi, band, sigma):
    """ Creates a guassian rectangular window function where any values 
    outside of the band follows a gaussian.

    Parameters
    ----------
    f : array of floats
        Frequency range.
    fi : float
        Central frequency of the band.
    band : float
        Half-width of the band.
    sigma : float
        Rate of the decline of gaussian out-of-band.

    Returns
    -------
    final_values : array of floats
        Final values after applying the gaussian attenuation.
    """

    def gauss(x,b,c):
        return np.exp( -((x-b)**2) / (2*c**2) )
    final_values = np.ones(len(f))

    # subtituting values where f is above the band
    mask_high = (f>=fi+band)
    idx_high = np.where(mask_high)[0]
    if len(idx_high)!=0:  final_values[idx_high] = gauss(f[idx_high], b=f[idx_high[0]], c=sigma)

    # substituting values where f is below the band
    mask_low = (f<=fi-band)
    idx_low = np.where(mask_low)[0]
    if len(idx_low)!=0:
        final_values[idx_low] = gauss(f[idx_low], b=f[idx_low[-1]], c=sigma)

    return final_values


