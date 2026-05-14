
# ----------------------------------------------- #
## ------------------- IMPORTS ----------------- ##
# ----------------------------------------------- #

import pickle
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import astropy.constants as cc
from fractions import Fraction
from satellite_RFI.src import psd_models
from scipy.optimize import lsq_linear


# ----------------------------------------------- #
## ------------------ FUNCTIONS ---------------- ##
# ----------------------------------------------- #

def CF_radiometer(alphas,sat):
    ''' Computes CF for the given alphas, with weights=obs (case C1). '''
    sat.execute(alphas)
    CF = np.sum( ((sat.observations_sat-sat.simulation) / sat.observations)**2 )
    print(CF,end="\t")
    return CF

# ----------------------------------------------- #

def CF_unweighted(alphas,sat):
    ''' Computes CF for the given alphas, with weights=1 (case C2). '''
    sat.execute(alphas)
    CF = np.sum( (sat.observations_sat-sat.simulation)**2 )
    print(CF,end="\t")
    return CF

# ----------------------------------------------- #

def _floaty(x):
    """ Auxiliary function for values stored as floats or fractions. """
    try:  return float(x)
    except ValueError:  return float(Fraction(x))

# ----------------------------------------------- #
## --------- CLASS SATELLITESIMULATION --------- ##
# ----------------------------------------------- #

class SatelliteSimulation:
    """
    An object which calculates the comparison between the Observational TOD and the simulated TOD.
    
    Attributes (external)
    ----------
    catalog : pandas DataFrame
    observations : tensor
    observations_BG : tensor
    observations_sat : tensor
    simulation : tensor
        

    Functions (external)
    ---------
    __init__: Initializes the simulation instance.
    create_mask: Creates a mask given the parameters.
    execute: Calculates the simulation for a given set of alpha values.
    execute_withmask: Same as execute, but applies the mask (necessary when we are only visualizing results).
    update_alphas: Updates the internal catalog with the alpha values given.
    """

    # ----------------------------------------------- #
    
    def __init__(self, block=None, use_data=True, path_data=None, path_beam=None, survey_info=None, path_catalog=None, 
                 beam_model=None, freq_range=None, freq_slice=None, time_slice=None, include_cons=None, verbose=False):
        ''' Initializes the simulation with some attributes and calculates everything that doesn't require alphas. '''

        # saving attributes
        self.block = block
        self.use_data = use_data
        self.nd_s0, self.frequency = (survey_info[0],survey_info[2])
        self.include_cons = include_cons

        # getting catalog data for the specific constellations and frequency slice
        print("Getting catalog...")
        catalog = pd.read_csv(path_catalog, header=0, engine="python")
        catalog = catalog[catalog["Sys"].str.contains("|".join(include_cons))]
        catalog = catalog[catalog["Frequency[MHz]"] >= freq_slice[0]]
        catalog = catalog[catalog["Frequency[MHz]"] <= freq_slice[1]]
        if verbose:  print("Number of signals in satellite catalog: ", len(catalog))
        self.catalog = catalog

        # getting frequency range, time slice, and frequency slice
        idx_freq_range = self._cut_range(self.frequency, freq_range)
        self.frequency = self.frequency[idx_freq_range[0] : idx_freq_range[1]]
        self.ifreq = self._cut_range(self.frequency, freq_slice)
        
        # getting beam response (B/r**2, summed for all satellites in a given constellation)
        print("Getting beam response (2GB) ...")
        self.cons,self.sat_beam = self._get_beam_response(path_beam, beam_model, freq_range)
        if verbose:  print("Number of constellations present: ", len(self.cons))

        # calculating satellite temperature factors for each signal (independent of alphas)
        # DIFERENTE, VERIFICAR QUE FUNCIONA!
        print("Getting temperature factors for each signal...")
        self.Tb_factors = self._get_Tb_factors()

        # counting number of signals in each constellation and starting index of constellations
        # DIFERENTE, VERIFICAR QUE FUNCIONA!
        self.n_signals = np.array([len(catalog[catalog["Sys"].str.contains(s)]) for s in self.cons])
        self.index_cons = np.concatenate(([0], np.cumsum(self.n_signals)[:-1]))
        if verbose:  print("Starting index of constellations: ", self.index_cons)

        # getting observational data
        print("Getting observational data...")
        if use_data:  
            self.observations, self.observations_BG = self._get_observations(path_data)  # <-- already sliced!
            self.observations_sat = self.observations - self.observations_BG

        # time interval
        self.itime = self._cut_range(self.nd_s0, time_slice)
        if time_slice is not None:
            self.sat_beam = self.sat_beam[:, :, self.itime[0]:self.itime[1]]
            self.observations = self.observations[:, self.itime[0]:self.itime[1]]
            self.observations_sat = self.observations_sat[:, self.itime[0]:self.itime[1]]
            self.observations_BG = self.observations_BG[:, self.itime[0]:self.itime[1]]
        
    # ----------------------------------------------- #

    def create_mask(self, path_nearby=None, temperature=None, pix=None, apply=True, verbose=False):
        ''' Creates the mask and applies itime to sat_beam and observations_sat. '''

        # initial parameters
        mask = np.ones_like(self.observations, dtype=bool)

        # angular mask
        if path_nearby is not None:
            f = pickle.load(open(path_nearby, "rb"), encoding="latin1")
            nearby_cons, nearby_times = self._filter_cons(list(f.keys()), list(f.values()))
            mask_degree = np.ones((len(self.frequency),len(self.nd_s0)), dtype=bool)
            for idx,c in enumerate(nearby_cons):  mask_degree[:, nearby_times[idx]] = False
            mask_degree = mask_degree[self.ifreq[0]:self.ifreq[1], self.itime[0]:self.itime[1]]
            mask = (mask & mask_degree)

        # temperature mask
        if temperature is not None:
            mask_temperature = np.where(self.observations <= temperature, True, False)
            mask = (mask & mask_temperature)

        # pixel timeline mask
        if pix is not None:
            threshold = np.max(self.observations)/pix
            mask_pix = np.where(self.observations <= threshold, True, False)
            mask_pix = (mask_pix & np.all(mask_pix,axis=0))
            mask = (mask & mask_pix)
        
        # applying mask to the matrices
        self.mask = mask
        if apply:
            self.sat_beam *= mask   # <-- simulation
            self.observations_sat *= mask   # <-- observations

        # plotting
        if verbose:
            plt.imshow(np.ma.masked_equal(self.observations.T * self.mask.T,0), aspect="auto")
            plt.title("Masked observations_sat")
            plt.colorbar()
            plt.show()
            print("Size of arrays:")
            print(" - Frequency: ", np.shape(self.frequency[self.ifreq[0]:self.ifreq[1]]))  # <-- frequency
            print(" - Time: ", np.shape(self.nd_s0[self.itime[0]:self.itime[1]]))  # <-- time
            print(" - Size of simulated Tb_factors: ", np.shape(self.Tb_factors))  # <-- signals x frequency
            print(" - Size of simulated sat_beam: ", np.shape(self.sat_beam))  # <-- cons x frequency x time
            print(" - Size of observations: ", np.shape(self.observations))  # <-- frequency x time
                
    # ----------------------------------------------- #
    
    def execute(self, alphas):
        ''' Calculates the simulation using the alphas given. '''

        # calculating simulation
        power_term = np.add.reduceat(self.Tb_factors*alphas[:,np.newaxis], self.index_cons, axis=0)
        self.simulation = np.einsum('kij,ki->ij', self.sat_beam, power_term)

    # ----------------------------------------------- #
    
    def execute_withmask(self, alphas):
        ''' Calculates the simulation using the alphas given, and masking the simulation (if not done prior!). '''

        # calculating simulation
        power_term = np.add.reduceat(self.Tb_factors*alphas[:,np.newaxis], self.index_cons, axis=0)
        self.simulation = np.einsum('kij,ki->ij', self.sat_beam*self.mask, power_term)

    # ----------------------------------------------- #

    def optimize_alphas_LS(self, CF):  
        ''' Find optimal alphas with least squares weighted or not, 
        by solving the linear problem |A*alpha - b|^2 with lsq_linear. '''

        # creating matrix A
        print("Creating matrix A and b ...")
        A = np.empty((self.observations_sat.size, len(self.catalog)))
        for k in range(len(self.catalog)):
            alphas = np.zeros(len(self.catalog))
            alphas[k] = 1.0
            self.execute(alphas)
            A[:,k] = self.simulation.ravel()
        b = self.observations_sat.ravel()

        # defining weights if necessary
        if CF=="C1":  
            print("Applying weights for CF=C1 ...")
            weights = 1.0 / self.observations.ravel()
            A *= weights[:,None]
            b *= weights

        print("Running optimization...")
        res = lsq_linear(
            A, b,         
            bounds=(0, np.inf), 
            verbose=2
        )
        return res

    # ----------------------------------------------- #

    def _cut_range(self, array, limits):
        ''' Get array cut within the specified limits. '''
        
        if limits[0] is None:  idx_start = 0
        else:  idx_start = np.where(array > limits[0])[0][0] - 1
        if limits[1] is None:  idx_end = -1  # <-- MAKES NO SENSE!
        else:  idx_end = np.where(array > limits[1])[0][0] + 1
        return [idx_start, idx_end]

    # ----------------------------------------------- #
    
    def _filter_cons(self, cons, array, turn_numpy=False):
        ''' Filter constellation list based on the include_cons list, ordered with include_cons order. '''

        if self.include_cons is None:  return cons, array
        
        cons_new, array_new = [], []
        for i,c in enumerate(cons):
            if c in self.include_cons: 
                cons_new.append(c)
                array_new.append(array[i])
        if turn_numpy:  return np.array(cons_new), np.array(array_new)
        return cons_new, array_new

    # ----------------------------------------------- #
    
    def _get_beam_response(self, path_beam, beam_model, freq_range):
        ''' Get B/r^2 for each constellation (function of frequency and time). '''

        # getting data
        f2 = pickle.load(open("{}{}_satellite_angular_position_{}_beam_{}_{}MHz.p".format(
            path_beam,self.block,beam_model,*freq_range),"rb",), encoding="latin1")

        # filtering constellations
        cons,sat_beam = self._filter_cons(f2["sat_name"], f2["angular"], turn_numpy=True)
        sat_beam = sat_beam[:, self.ifreq[0]:self.ifreq[1], :]
        return cons,sat_beam

    # ----------------------------------------------- #
    
    def _get_observations(self, path_data):
        """ Obtain the calibrated TOD for the temperature and the noise. """

        # getting data
        data = pickle.load(open(path_data + self.block + "_average_TOD_BG_model.p", "rb"),encoding="latin1",)
        observations = np.array(data["TOD Avg"].T)
        observations_BG = np.array(data["BG Model"].T)

        # cutting frequency interval
        observations = observations[self.ifreq[0]:self.ifreq[1], :]
        observations_BG = observations_BG[self.ifreq[0]:self.ifreq[1], :]
        return observations, observations_BG

    # ----------------------------------------------- #

    def _get_Tb_factors(self):
        ''' Returns the array of brightness temperature factors (functions 
        of frequency) for all signals of a given constellation. '''

        P = self.catalog["P_t (dBW)"]
        G = self.catalog["G_t (dBi)"]
    
        # calculating emitted power)
        value = 10**(P/10 + G/10) / (4*np.pi)
        power = np.where(P*G != 0, value, 0)
        SP = np.zeros( (len(self.catalog), len(self.frequency)) )
        
        # looping through each signal of the constellation
        for k,i in enumerate(self.catalog.index):
            
            # getting information
            m = self.catalog["Modulation"][i]
            fc = self.catalog["Frequency[MHz]"][i]
            rate = self.catalog["Rate(MHz)"][i]
            mtype = m.split("(")[0]
            params = m[m.find("(")+1 : m.find(")")].split(",")
    
            # calculating modulations
            if mtype=="BPSK":
                Tc = float(params[0])
                psd = psd_models.BPSK(f=self.frequency-fc, nc=Tc, f0=rate/Tc)
            elif mtype=="BOCcos":
                Ts, Tc = map(float, params)
                psd = psd_models.BOCc(f=self.frequency-fc, nc=Tc, ns=Ts, f0=rate/Tc)
            elif mtype=="AltBOC":
                Ts, Tc = map(float, params)
                psd = psd_models.altBOC(f=self.frequency-fc, ns=Ts, nc=Tc, f0=rate/Tc)
            elif mtype=="TMBOC":
                Ts, Tc, rt = [_floaty(x) for x in params]
                psd = psd_models.TMBOC(f=self.frequency-fc, nc=Tc, ns=Ts, f0=rate/Tc, ratio=rt)
            elif mtype=="CBOC":
                Ts, Tc, rt = [_floaty(x) for x in params]
                psd = psd_models.CBOC(f=self.frequency-fc, nc=Tc, ns=Ts, f0=rate/Tc, ratio=rt)
            elif mtype=="BOC":
                Ts, Tc = map(float, params)
                psd = psd_models.BOC(f=self.frequency-fc, nc=Tc, ns=Ts, f0=rate/Tc)
            psd = np.nan_to_num(psd, nan=0)
    
            # indexes are different because csv starts at 1, not 0
            SP[k] = power[k]*psd
    
        # getting terms from the equation
        delta_nu = 0.2 * 1e6  # <-- channel width in Hz (extra)
        factor = cc.c.value**2 / (cc.k_B.value * 4*np.pi * (self.frequency*1e6)**2)
        gain_factor = 1e4  # <-- gain factor from Harpar paper (extra)
    
        # final result in mK and cutting slice
        Tb_factors = SP * (factor*gain_factor/delta_nu)
        Tb_factors = Tb_factors[:, self.ifreq[0]:self.ifreq[1]]
        return Tb_factors

    # ----------------------------------------------- #

