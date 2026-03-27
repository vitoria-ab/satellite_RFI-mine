###################################################
# Functions for modulations of the PSD 
# - BPSK = BPSK(old); now cleaner
# - BOC = BOC(old); now cleaner
# - BOCc = BOCc(old); now cleaner
# - altBOC
# - MBOC
# - TMBOC
# - CBOC
###################################################

"""
2020/11/15
Contains the Power Spectrum Density Models for the GNSS satellites.
Informationg comes primarly from <Springer Handbook of GNSS; P.J.G Teunissen pg 100
"""

## ----- IMPORTS ----- ##
import numpy as np


## ----- FUNCTIONS ----- ##
def BPSK(f, nc, f0=1.023):
    """
    Binary Phase Switch Keying PSD (pg 107).

    Parameters
    ----------
    f : array of floats
        Frequency range, already corrected with the
        central frequency of the signal.
    nc : float
        Chip rate
    f0 : float (optional)
        Reference frequency (default is 1.023 MHz).

    Returns
    psd : array of floats
        PSD of the signal at each frequency.
    """
    tc = 1 / (nc*f0)
    P = np.sqrt(tc) * np.sinc(f * tc)
    psd = P**2
    return psd



def BOC(f, nc, ns, f0=1.023):
    """
    Binary Offset Carrier (Springer pg110).

    Parameters
    ----------
    f : array of floats
        Frequency range in MHz.
    ns : float
        Sub-carrier rate.
    nc : float
        Chip rate.
    f0 : float (optional)
        Reference frequency (default is 1.023 MHz).

    Returns
    -------
    psd : array of floats
        PSD of the signal at each frequency.
    """

    # checking if the rates are possible
    if ns < nc:  return np.zeros(len(f))

    # calculating initial quantities
    dfrac = f[1]-f[0]
    f1 = f - dfrac/2
    f2 = f + dfrac/2
    a = np.sqrt(nc*f0)

    # auxiliary function
    def calc(f, func):
        b = func( np.pi*f / (nc*f0) ) / (np.pi*f)
        c = np.tan( np.pi*f / (2*ns*f0) )
        return (a*b*c)**2

    # checking if it's odd or even
    N = 2.0*ns/nc
    if N%2 == 0:  func = np.sin
    else:  func = np.cos
    term1 = calc(f1, func)
    term2 = calc(f2, func)
    psd = 0.5 * (term1 + term2)

    return psd



def BOCc(f, nc, ns, f0=1.023):
    """
    Cosine Binary Offset Carrier (Springer pg110).

    Parameters
    ----------
    f : array of floats
        Frequency range in MHz.
    ns : float
        Sub-carrier rate.
    nc : float
        Chip rate.
    f0 : float (optional)
        Reference frequency (default is 1.023 MHz).

    Returns
    -------
    psd : array of floats
        PSD of the signal at each frequency.
    """

    # checking if the rates are possible
    if ns < nc:  return np.zeros(len(f))

    # calculating initial quantities
    dfrac = f[1]-f[0]
    f1 = f - dfrac/2
    f2 = f + dfrac/2
    a = np.sqrt(nc*f0)

    # auxiliary function
    def calc(f, func):
        b = func( np.pi*f / (nc*f0) ) / (np.pi*f)
        c = (1 - np.cos( np.pi*f / (2*ns*f0) )) / np.cos(np.pi*f / (2*ns*f0))
        return (a*b*c)**2

    # checking if it's odd or even
    N = 2.0*ns/nc
    if N%2 == 0:  func = np.sin
    else:  func = np.cos
    term1 = calc(f1, func)
    term2 = calc(f2, func)
    psd = 0.5 * (term1 + term2)

    return psd


# --------------------------------------------------------------------------------------#

# Missing AltBOC - Still require new version


def altBOC(f, nc, ns, f0):
    """
    Binary Offset Carrier (BOC). The altBOC name refers to use a QPSK multiplexing signal.
    The chip size of the BPSK signal (Tc) is larger and an integer value of the
    carrier signal chap size (Ts). Tc > Ts
    https://gssc.esa.int/navipedia/index.php/AltBOC_Modulation.
    n > m
    (Tc > Ts)
    """

    phi = 2 * ns / nc
    alp = 4 * nc * f0 / (np.pi * f) ** 2
    div = np.cos(np.pi * f / 2 / ns / f0) ** 2
    beta = (
        np.cos(np.pi * f / 2 / ns / f0) ** 2
        - np.cos(np.pi * f / 2 / ns / f0)
        - 2 * np.cos(np.pi * f / 2 / ns / f0) * np.cos(np.pi * f / 4 / ns / f0)
        + 2
    )

    if np.mod(phi, 2) == 0:  # Phi-even spectrum
        num = np.sin(np.pi * f / nc / f0) ** 2

    else:
        num = np.cos(np.pi * f / nc / f0) ** 2

    return alp * (num / div) * beta


# --------------------------------------------------------------------------------------#

# Missing MBOC - Still require new version


def MBOC(f, m, f0=1.023):
    """
    https://en.wikipedia.org/wiki/Multiplexed_binary_offset_carrier
    https://gssc.esa.int/navipedia/index.php/MBOC_Modulation
    """

    fc = m * f0

    A = fc / 11 / np.pi ** 2 / f ** 2
    B = np.sin(np.pi * f / fc) ** 2
    C = 10 * np.tan(np.pi * f / 2 / fc) ** 2
    D = np.tan(np.pi * f / 12 / fc) ** 2

    return A * B * (C + D)


# --------------------------------------------------------------------------------------#

# TMBOC


def TMBOC(f, nc, ns, f0, ratio):
    """
    Time Multiplexed BOC, same as CBOC?
    https://gssc.esa.int/navipedia/index.php/Time-Multiplexed_BOC_(TMBOC)
    See BOC for information guide.
    Ratio - the ratio in the power values
    """

    diff_ratio = 1.0 - ratio

    t1 = diff_ratio * BOC(f=f, nc=nc, ns=1, f0=f0)
    t2 = ratio * BOC(f=f, nc=1, ns=ns, f0=f0)

    return t1 + t2


# --------------------------------------------------------------------------------------#

# TMBOC


def CBOC(f, nc, ns, f0, ratio):
    """
    Composite BOC
    See BOC for information guide.
    Ratio - the ratio in the power values
    https://www.dlr.de/kn/Portaldata/27/Resources/dokumente/06_projekte/Loh_PLANS2010.pdf  Eq.3
    
    """

    diff_ratio = 1.0 - ratio

    t1 = np.sqrt(diff_ratio) * BOC(f=f, nc=nc, ns=1, f0=f0)
    t2 = np.sqrt(ratio) * BOC(f=f, nc=1, ns=ns, f0=f0)

    return t1 + t2


# --------------------------------------------------------------------------------------#
