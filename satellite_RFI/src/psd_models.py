"""
Defines functions for the Power Spectrum Density (PSD) models for the GNSS satellite signals; Sxx = |P|^2 given in Eq. 3. Information comes primarily from 'Springer Handbook of GNSS' (pages 107-113) and from several Navipedia pages. Instead of using directly chip rates (given in the signal catalog), they use the modulation specifiers nc in order to derive the chip rate (it's more numerically exact, using integers).

Functions
---------
- BPSK = BPSK(old); the same. 
- BOC = BOC(old); now uses directly Springer's formula.
- BOCcos = BOCc(old); now uses directly Springer's formula.
- AltBOC = altBOC(old); the same.
- MBOC = MBOC(old); now uses Navipedia's formula.
- TMBOC = TMBOC(old); now same as MBOC.
- CBOC = CBOC(old); now same as MBOC.
"""


## --------------- IMPORTS --------------- ##
import numpy as np


## --------------- FUNCTIONS --------------- ##
def BPSK(f, nc, f0=1.023):
    """
    Binary Phase Switch Keying PSD (Springer page 107).

    Parameters
    ----------
    f : array of floats
        Frequency range (needs to be already corrected with 
        the central frequency of the signal).
    nc : int
        Chip rate.
    f0 : float (optional)
        Reference frequency (default is 1.023 MHz).

    Returns
    PSD : array of floats
        PSD of the signal at each frequency.
    """
    Tc = 1 / (nc*f0)
    return Tc * np.sinc(f*Tc)**2


## ---------------------------------------- ##
def BOC(f, ns, nc, f0=1.023):
    """
    Binary Offset Carrier PSD (Spring page 110).

    Parameters
    ----------
    f : array of floats
        Frequency range in MHz.
    ns : int
        Sub-carrier rate.
    nc : int
        Chip rate.
    f0 : float (optional)
        Reference frequency (default is 1.023 MHz).

    Returns
    -------
    PSD : array of floats
        PSD of the signal at each frequency.
    """

    # initial quantities
    if (2*ns/nc)%2==0:  func = np.sin
    elif (2*ns/nc)%2==1:  func = np.cos
    arg1 = np.pi/(2*ns*f0)
    arg2 = np.pi/(nc*f0)

    # calculating PSD
    if (ns==2*nc):  # <-- in this case there is a 0/0 error at f=k*pi/2 which gives a non-null value
        with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
            temp = 4*np.cos(1/2*arg2*f)/f * np.sin(arg2*f/4)**2
    else:
        with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
            temp = np.tan(arg1*f)/f * func(arg2*f)
        temp[((arg1*f)%(np.pi/2)<1e-10)] = 0   # <-- f=k*pi/2, gives an error due to tan(f)
    temp[f==0] = 0   # <-- f=0, gives an error due to 1/f
    
    return (nc*f0)/np.pi**2 * temp**2


## ---------------------------------------- ##
def BOCcos(f, ns, nc, f0=1.023):
    """
    Cosine Binary Offset Carrier PSD (Springer page 110). 
    Needs to be rewritten to deal with possible null values!!

    Parameters
    ----------
    f : array of floats
        Frequency range in MHz.
    ns : int
        Sub-carrier rate.
    nc : int
        Chip rate.
    f0 : float (optional)
        Reference frequency (default is 1.023 MHz).

    Returns
    -------
    PSD : array of floats
        PSD of the signal at each frequency.
    """

    # initial quantities
    if (2*ns/nc)%2==0:  func = np.sin
    elif (2*ns/nc)%2==1:  func = np.cos

    # calculating PSD
    arg1 = np.pi*f/(nc*f0)
    arg2 = np.pi*f/(2*ns*f0)
    Pabs = np.sqrt(nc*f0) * func(arg1)/(np.pi*f) * (1-np.cos(arg2))/np.cos(arg2)
    return Pabs**2


## ---------------------------------------- ##
def MBOC(f, nsA, nsB, ratio, f0=1.023):
    ''' 
    Multiplexed Binary Offset Carrier PSD (Springer page 112);
    both TMBOC and CBOC have PSDs given by this expression.
    
    Parameters
    ----------
    f : array of floats
        Frequency range in MHz.
    nsA : int
        Sub-carrier rate of the first signal.
    nsB : int
        Sub-carrier rate of the second signal.
    ratio : float
        PSD fraction of the first signal.
    f0 : float (optional)
        Reference frequency (default is 1.023 MHz).

    Returns
    -------
    PSD : array of floats
        PSD of the signal at each frequency.
    '''

    term1 = ratio * BOC(f, nsA, 1, f0)
    term2 = (1-ratio) * BOC(f, nsB, 1, f0)
    return term1 + term2


## ---------------------------------------- ##
def CBOC(f, nsA, nsB, ratio, f0=1.023):
    ''' Composite Binary Offset Carrier PDS; returns MBOC PSD. '''
    return MBOC(f, nsA, nsB, ratio, f0)


## ---------------------------------------- ##
def TMBOC(f, nsA, nsB, ratio, f0=1.023):
    ''' Time-multiplexed Binary Offset Carrier PDS; returns MBOC PSD. '''
    return MBOC(f, nsA, nsB, ratio, f0)


## ---------------------------------------- ##
def AltBOC(f, ns, nc, f0=1.023):
    ''' 
    Alternative Binary Offset Carrier PDS (Springer page 113; source is
    https://gssc.esa.int/navipedia/index.php/AltBOC_Modulation). 
    
    Parameters
    ----------
    f : array of floats
        Frequency range in MHz.
    ns : int
        Sub-carrier rate.
    nc : int
        Chip rate.
    f0 : float (optional)
        Reference frequency (default is 1.023 MHz).

    Returns
    -------
    PSD : array of floats
        PSD of the signal at each frequency.
    '''
    
    # initial quantities
    if (2*ns/nc)%2==0:  func = np.sin
    elif (2*ns/nc)%2==1:  func = np.cos
    arg1 = np.pi*f/(nc*f0)
    arg2 = np.pi*f/(2*ns*f0)

    # calculating PSD
    term1 = 4*nc*f0/(np.pi*f)**2
    term2 = (func(arg1)/np.cos(arg2))**2
    term3 = np.cos(arg2)**2 - np.cos(arg2) - 2*np.cos(arg2)*np.cos(arg2/2) + 2
    return term1*term2*term3

