"""
Defines the satellite simulation class, which aggregates all of the information so far. Considers the case where all satellites are treated individually, with the new catalog.

Functions
---------
_floaty(x)

Classes
-------
SatelliteSimulation
    __init__(self, survey_info=None, path_catalog=None, path_beam=None, freq_range=None, 
    freq_slice=None, time_slice=None, verbose=False)
    use_observations(self, path_observations, verbose=True)
    use_mask(self, deg=None, temp=None, pix=None, apply=True, verbose=False)
    simulate(self, alphas)
    simulate_withmask(self, alphas)
    _cut_range(self, array, limits)
    _get_Tb_factors(self)
"""

# -------------------------------------------------- #
## -------------------- IMPORTS ------------------- ##
# -------------------------------------------------- #

import pickle
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import astropy.constants as cc
from fractions import Fraction
from satellite_RFI.src import psd_models


# -------------------------------------------------- #
## ------------------- FUNCTIONS ------------------ ##
# -------------------------------------------------- #

def _floaty(x):
    """ Auxiliary function for values stored as floats or fractions. """
    try:  return float(x)
    except ValueError:  return float(Fraction(x))

# -------------------------------------------------- #
## ---------- CLASS SatelliteSimulation ----------- ##
# -------------------------------------------------- #

class SatelliteSimulation:
    """
    An object which calculates the comparison between the Observational TOD and the simulated TOD.
    
    Attributes (external)
    ----------
    catalog : pandas DataFrame
    obs : tensor
    BG : tensor
    obs_BGsub : tensor
    sim : tensor
        

    Functions (external)
    ---------
    __init__: Initializes the simulation instance.
    use_observations : Includes observations in the object.
    use_mask: Creates a mask given the parameters.
    simulate: Calculates the simulation for a given set of alpha values.
    simulate_withmask: Same as simulate, but applies the mask (necessary when we are only visualizing results).
    """

    # -------------------------------------------------- #
    
    def __init__(self, survey_info=None, path_catalog=None, path_beam=None, freq_range=None, 
                 freq_slice=None, time_slice=None, verbose=False, label_sats="NORAD ID"):
        ''' Initializes the simulation with some attributes and calculates everything that doesn't require alphas. '''

        # saving attributes
        self.time, self.frequency = (survey_info[0],survey_info[1]) 

        # getting catalog data for the specific constellations and frequency slice
        if verbose:  print("Getting catalog...\n - Number of signals in satellite catalog: ",end="")
        catalog = pd.read_csv(path_catalog, header=0, engine="python")
        if verbose:  print(f"{len(catalog)} (initial), ",end="")
        catalog = catalog[catalog["Frequency(MHz)"] >= freq_slice[0]]
        catalog = catalog[catalog["Frequency(MHz)"] <= freq_slice[1]]
        if verbose:  print(f"{len(catalog)} (final).")
        self.catalog = catalog

        # getting frequency range, time slice, and frequency slice
        idx_freq_range = self._cut_range(self.frequency, freq_range)
        self.frequency = self.frequency[idx_freq_range[0] : idx_freq_range[1]]
        self.ifreq = self._cut_range(self.frequency, freq_slice)
        self.itime = self._cut_range(self.time, time_slice)
        if verbose:
            t = self.time[self.itime[0]:self.itime[1]]
            f = self.frequency[self.ifreq[0]:self.ifreq[1]]
            print(f" - Shape of dimensions is Nt,Nf = {len(t)},{len(f)}")
        
        # getting beam response (B/r**2)
        if verbose:  print("Getting beam response...")
        f2 = pickle.load(open(path_beam,"rb",), encoding="latin1")
        self.sat_beam = np.array(list(f2.values()))[:, 
            self.ifreq[0]:self.ifreq[1], self.itime[0]:self.itime[1]]
        self.sats = list(f2.keys())
        if verbose:  
            print(f" - Number of satellites present: {len(self.sats)}")
            print(f" - Size of sat_beam: {self.sat_beam.nbytes / 1024**3:.3f} GB")
        
        # getting satellite temperature factors for each signal (independent of alphas)
        if verbose:  print("Getting temperature factors for each signal...")
        self.Tb_factors = self._get_Tb_factors()
        if verbose:  
            print(f" - Length of Tb_factors: {len(self.Tb_factors)}")
            print(f" - Size of Tb_factors: {self.Tb_factors.nbytes / 1024**3:.3f} GB")

        # counting number of signals in each satellite and starting index of satellites
        self.n_signals = np.array([len(catalog[catalog[label_sats]==sat]) for sat in self.sats])
        self.index_sats = np.concatenate(([0], np.cumsum(self.n_signals)[:-1]))
        self.tmp = np.empty_like(self.Tb_factors)  # <-- useful to spare memory
        self.tmp2 = np.zeros((len(self.sats),np.shape(self.Tb_factors)[1]))  # <-- useful to spare memory
        return

        
    # -------------------------------------------------- #

    def use_observations(self, path_observations, verbose=True):
        ''' Includes observational data in the simulation object. '''

        # getting observational data
        if verbose:  print("Getting observational data...")
        data = pickle.load(open(path_observations, "rb"),encoding="latin1",)

        # cutting time and frequency slices
        self.obs = np.array(data["TOD Avg"].T)[self.ifreq[0]:self.ifreq[1], self.itime[0]:self.itime[1]]
        self.BG = np.array(data["BG Model"].T)[self.ifreq[0]:self.ifreq[1], self.itime[0]:self.itime[1]]
        self.obs_BGsub = self.obs - self.BG
        if verbose:  
            print(f" - Size of observational data: {self.obs.nbytes / 1024**3:.3f} GB")
            print(f" - Shape of observational data: {np.shape(self.obs)}")
        return

        
    # -------------------------------------------------- #
    
    def use_mask(self, deg=None, temp=None, pix=None, apply=True, verbose=False):
        ''' Creates the mask and applies itime to sat_beam and obs_BGsub. '''

        # initial parameters
        mask = np.ones_like(self.obs, dtype=bool) 

        # angular mask ("deg" is the times indexes where a satellites comes nearby)
        if deg is not None: 
            mask_degree = np.ones((len(self.frequency),len(self.time)), dtype=bool) 
            mask_degree[:, deg] = False
            mask_degree = mask_degree[self.ifreq[0]:self.ifreq[1], self.itime[0]:self.itime[1]] 
            mask = (mask & mask_degree) 

        # temperature mask
        if temp is not None:
            mask_temperature = np.where(self.obs <= temp, True, False) 
            mask = (mask & mask_temperature)

        # pixel timeline mask
        if pix is not None:
            threshold = np.max(self.obs)/pix
            mask_pix = np.where(self.obs <= threshold, True, False)
            mask_pix = (mask_pix & np.all(mask_pix,axis=0))
            mask = (mask & mask_pix)

        # checking if any pixels are faulty
        bad_pixels = (self.obs<=0)
        mask[bad_pixels] = False
        self.obs[bad_pixels] = 1  # <-- to prevent division by zero
        
        # applying mask to the matrices
        self.mask = mask
        if apply:
            self.sat_beam *= mask   # <-- simulation
            self.obs_BGsub *= mask   # <-- observations

        # plotting
        if verbose:
            freq = self.frequency[self.ifreq[0]:self.ifreq[-1]]
            t = self.time[self.itime[0]:self.itime[-1]]
            dplot = np.ma.masked_array(self.obs_BGsub.T, mask=~self.mask.T)
            plt.imshow(dplot, extent=[freq[0],freq[-1],t[-1],t[0]], aspect="auto")
            plt.colorbar()
            plt.show()

            
    # -------------------------------------------------- #
    
    def simulate(self, alphas):
        ''' Calculates the simulation using the alphas given. '''

        # calculating simulation
        np.multiply(self.Tb_factors, alphas[:,None], out=self.tmp)
        self.tmp2.fill(0)
        for i_sat, start in enumerate(self.index_sats):
            stop = start + self.n_signals[i_sat]
            if stop>start:  self.tmp2[i_sat] = np.sum(self.tmp[start:stop], axis=0)
        #np.add.reduceat(self.tmp, self.index_sats, axis=0, out=self.tmp2)
        self.sim = np.einsum('kij,ki->ij', self.sat_beam*self.mask, self.tmp2)

        
    # -------------------------------------------------- #
    
    def _cut_range(self, array, limits):
        ''' Get array cut within the specified limits; for now, this way (which is a bit weird) will 
        have to do since the beam model is already pre-cut during N2 using this exact way. '''
        
        if limits[0] is None:  idx_start = None
        else:  idx_start = np.where(array > limits[0])[0][0] - 1
        if limits[1] is None:  idx_end = None
        else:  idx_end = np.where(array > limits[1])[0][0] + 1
        return [idx_start, idx_end]

        
    # -------------------------------------------------- #
    
    def _get_Tb_factors(self):
        ''' Returns the array of brightness temperature factors (functions 
        of frequency) for all signals. '''

        P = self.catalog["P(dBW)"] 
        G = self.catalog["G(dBi)"] 
    
        # calculating emitted power
        power = 10**(P/10 + G/10) / (4*np.pi)
        freq = self.frequency[self.ifreq[0]:self.ifreq[1]]  # <-- already cut from the beginning
        SP = np.zeros( (len(self.catalog), len(freq)) )
         
        # looping through each signal of the constellation
        for i,ind in enumerate(self.catalog.index):
            
            # getting information
            m = self.catalog["Modulation"][ind]
            fc = self.catalog["Frequency(MHz)"][ind]
            mtype = m.split("(")[0]
            params = m[m.find("(")+1 : m.find(")")].split(",")
    
            # calculating modulations
            if mtype=="BPSK":
                nc = float(params[0])
                psd = psd_models.BPSK(freq-fc, nc)
            elif mtype=="BOCcos":
                ns, nc = map(float, params)
                psd = psd_models.BOCcos(freq-fc, ns, nc)
            elif mtype=="AltBOC":
                ns, nc = map(float, params)
                psd = psd_models.AltBOC(freq-fc, ns, nc)
            elif mtype=="MBOC":
                nsA, nsB, ratio = [_floaty(x) for x in params]
                psd = psd_models.TMBOC(freq-fc, nsA, nsB, ratio)
            elif mtype=="BOC":
                ns, nc = map(float, params)
                psd = psd_models.BOC(freq-fc, ns, nc)
            else:
                print("Error: Signal modulation {} is not valid.".format(mtype))
            psd = np.nan_to_num(psd, nan=0)
    
            # indexes are different because csv starts at 1, not 0
            SP[i] = power[ind]*psd
    
        # getting terms from the equation
        delta_nu = 0.2 * 1e6  # <-- channel width in Hz (extra)
        factor = cc.c.value**2 / (cc.k_B.value * 4*np.pi * (freq*1e6)**2)
        gain_factor = 1e4  # <-- gain factor from Harpar paper (extra)
    
        # final result in mK
        return SP * factor * gain_factor / delta_nu


    # -------------------------------------------------- #

