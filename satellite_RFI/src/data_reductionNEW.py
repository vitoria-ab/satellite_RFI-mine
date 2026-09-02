"""
Defines the data reduction class, which performs the calibration to MeerKAT data. 

Functions
---------

Classes
-------
DataReduction
    __init__(self, )
    (...)
"""


# -------------------------------------------------- #
## -------------------- IMPORTS ------------------- ##
# -------------------------------------------------- #

# time packages
from datetime import datetime
# file packages
import pickle
# mathematical packages
import numpy as np
from scipy.interpolate import Rbf as Rbf
import scipy as sp
from astropy.stats import SigmaClip


# -------------------------------------------------- #
## ------------------- FUNCTION ------------------- ##
# -------------------------------------------------- #

def generate_katdal_file(block, verbose=False):
    '''Generates katdal information file (requires python2).'''

    # getting observational data from katdal
    if verbose:  print("Getting file with katdal...")
    import katdal
    KATSDPTELSTATE_ALLOW_PICKLE = 1  # <-- disables a legacy warning
    folders = {1551055211: "SCI-20180330-MS-01"}
    path = "/idia/projects/hi_im/MEERKLASS-1/raw_data/{}/{}/{}/".format(folders[block],block,block)
    obs_data = katdal.open(path + "{}_sdp_l0.full.rdb".format(block))

    # getting frequency and time
    frequency = np.round(obs_data.freqs / 1e6, 1)

    # getting noise diodes and timestamps -- RE-DO THE FILE LATER IF POSSIBLE!
    if verbose:  print("Getting nd timestamps...")
    path = "/idia/projects/hi_im/satellite_rfi/Testing/{}/{}".format(block,block)
    time,az,el,RA,DEC = np.load(path + "_Time_Pos.npy")
    nd_off = np.load(path + "_nd_S0.npy")
    nd_off_inds = np.array([np.where(i == time)[0][0] for i in nd_off[1]])

    # final parameters
    nd_s0 = nd_off[1] - block
    nd_s0_pos = np.array(nd_off[0], dtype="int64")
    nd_s = time - block
    nd_s0_coords = (az[nd_off_inds], el[nd_off_inds])
    nd_s0_coords2 = (RA[nd_off_inds], DEC[nd_off_inds])

    # creating katdal dictionary
    katdal_info = {"nd_s0":nd_s0, 
                   "nd_s0_pos":nd_s0_pos, 
                   "nd_s0_coords":nd_s0_coords, 
                   "nd_s0_coords2":nd_s0_coords2, 
                   "frequency":frequency} 
    return katdal_info, obs_data


# -------------------------------------------------- #

def _clean_outliers(data):
    """ Auxiliary function; masks frequency channels 
    containing values outside 3sigma of the mean. """

    # (I THINK THIS IS JUST MASKING THE ZERO VALUES... IF SO, REMOVE THIS!)
    mean=np.ma.mean(data);  std=np.ma.std(data)
    outliers = (data < mean-3*std) | (data > mean+3*std)
    channels = np.unique(np.ma.where(outliers)[1])
    data.mask[:, channels] = True
    return data


# -------------------------------------------------- #
## ------------- CLASS DataReduction -------------- ##
# -------------------------------------------------- #

class DataReduction:

    """
    An object which calibrates the MeerKAT data.
    
    Attributes (external)
    ----------
    catalog : pandas DataFrame
        

    Functions (external)
    ---------
    __init__: Initializes the simulation instance.
    """

    # -------------------------------------------------- #
    
    def __init__(self, block, path_cali, freq_range):
        ''' Initialization of the data reduction object. '''
        
        # setting some quantities
        self.block = block
        folders = {1551055211: "SCI-20180330-MS-01"}
        self.folder = folders[block]

        # getting katdal information
        katdal = pickle.load(open(path_cali + "katdal_info.p","rb"), encoding="latin1")
        self.nd_s0 = katdal["nd_s0"]
        self.nd_s0_coords = katdal["nd_s0_coords"]
        self.nd_s0_coords2 = katdal["nd_s0_coords2"]
        self.nd_s0_pos = katdal["nd_s0_pos"]
        self.frequency = katdal["frequency"]

        # getting antennas' names and frequency
        antennas = pickle.load(open(path_cali + "antennas.p","rb"), encoding="latin1")
        self.antennas = [str(ant)[:4] for ant in antennas]

        # getting frequency interval
        idx_start = np.where(self.frequency > freq_range[0])[0][0] - 1
        idx_end = np.where(self.frequency > freq_range[1])[0][0] + 1
        self.ifreq = [idx_start,idx_end]
        self.frequency_cut = self.frequency[self.ifreq[0]:self.ifreq[1]]
        return

    
    # -------------------------------------------------- #

    def get_background_raws(self, mask_level=False, N_debug=None):
        ''' Retrieves the raw background model files. '''

        # setting initial quantities
        Trec,Tgal,Tmap,good_antennas,mask = [],[],[],[],[]
        path = "/idia/projects/hi_im/raw_vis/katcali_output/"
        
        # iterate over the different antennas
        print("Retrieving data from antennas...")
        for ant in self.antennas[:N_debug]:

            # getting data information
            try:
                path3 = path + "level3_output/{}_{}".format(self.block,ant)
                data3H = pickle.load(open(path3 + "h_level3_data","rb"), encoding="latin1")
                data3V = pickle.load(open(path3 + "v_level3_data","rb"), encoding="latin1")
            except IOError:
                print("\tAntenna {} data (level 3) missing!".format(ant))
                continue

            # getting mask information
            try:
                # level 4
                if mask_level=="L4":
                    path4 = path + "level4_output/mask/{}_{}_level4_mask".format(self.block,ant)
                    data4 = pickle.load(open(path4,"rb"), encoding="latin1")["Inten_mask"]
                    mask.append(data4[self.nd_s0_pos,self.ifreq[0]:self.ifreq[1]])
                # level 6
                elif mask_level=="L6":
                    pix = "p{}d".format(0.3)
                    sig = "sigma_{}".format(2.5)
                    it = "iter{}".format(2)
                    path6 = (path + "level6_output/{}/{}_{}_{}/mask/{}".format(pix,pix,sig,it,self.block) 
                             + "{}_{}_level6_p{}d_sigma{}_iter{}_mask".format(ant,pix,sig,it))
                    data6 = pickle.load(open(path6,"rb"), encoding="latin1")["ch_mask"]
                    mask.append(data6[self.ifreq[0]:self.ifreq[1]])
                # no mask
                else:
                    mask.append(False)
            except IOError:
                print("\tAntenna {} mask (level 4/6) missing!".format(ant))
                continue

            # saving information
            print("\tAntenna {} successful.".format(ant))
            Trec.append([data3H['Tsm_map'][self.nd_s0_pos, self.ifreq[0]:self.ifreq[1]],
                         data3V['Tsm_map'][self.nd_s0_pos, self.ifreq[0]:self.ifreq[1]]])
            Tgal.append([data3H['Tgal_map'][self.nd_s0_pos, self.ifreq[0]:self.ifreq[1]],
                         data3V['Tgal_map'][self.nd_s0_pos, self.ifreq[0]:self.ifreq[1]]])
            Tmap.append([data3H['T_map'][self.nd_s0_pos, self.ifreq[0]:self.ifreq[1]],
                        data3V['T_map'][self.nd_s0_pos, self.ifreq[0]:self.ifreq[1]]])
            good_antennas.append(ant)

        # changing data types
        self.good_antennas = good_antennas
        return np.array(Trec),np.array(Tgal),np.array(Tmap),np.array(mask)


    # -------------------------------------------------- #

    def correct_Trec(self, Trec, mask):
        ''' Interpolate Trec for the given data (of a 
        specific antenna and polarization). '''

        # applying mask and creating separating variables
        # zero mask makes for a smoother curve than level 4, with almost the same format
        T = np.ma.masked_equal(Trec,0)
        Trec_t = np.ma.mean(T, axis=1)[:,None] / np.ma.mean(T)

        # interpolating the valid frequency spectrum
        # (CAN I USE A NEWER, PREFERABLE METHOD FOR THE INTERPOLATION?)
        Trec_f = np.ma.mean(np.ma.masked_array(Trec, mask=mask), axis=0)
        freq_idx = np.where(~Trec_f.mask)[0]
        func = Rbf(self.frequency_cut[freq_idx], Trec_f[freq_idx], 
                      function="linear", smooth=10)
        Trec_f_interp = func(self.frequency_cut)[None,:]

        # reconstructing full Trec TOD
        Trec_final = Trec_t * Trec_f_interp
        return Trec_final, freq_idx


    # -------------------------------------------------- #

    def correct_Tel(self, Tel):
        ''' Correct elevation temperature for a specific antenna; 
        if a spike is found, it interpolates on that region. Only 
        works if the data has one individual spike! '''

        # checking spikes only in the first timestamp
        threshold = 2
        spike = np.abs(np.diff(Tel[:,0])) > threshold

        # if there is one spike, rewrite that section
        if not np.any(spike):  spike_found = False
            
        else:
            # select valid sections
            print("One spike in the elevation data!")
            idx_start,idx_end = np.where(spike)[0][[0,-1]]
            valid = np.ones(Tel.shape[0], dtype=bool)
            valid[idx_start:idx_end + 1] = False

            # get arrays and interpolate
            Tel_valid = Tel[valid,0]
            nd_s0_valid = self.nd_s0[valid]
            func = Rbf(nd_s0_valid,Tel_valid)

            # get final array normalized
            # (THIS ASSUMES THE FREQUENCY DEPENDENCE IS THE SAME AS
            # IN INDEX 0; MAYBE TIME-AVERAGE WOULD BE BETTER!)
            Tel_f = Tel[0,:] / np.max(Tel[0,:])
            Tel = Tel_f[None,:] * func(self.nd_s0)[:,None]
            spike_found = True

        return Tel, spike_found


    # -------------------------------------------------- #

    def get_gain_raws(self, ant, masked=True):
        ''' Extracts the visibilities and gains of a given 
        antenna and performs some initial corrections.
        NOTE: "mask" was created because Brandon did these 
        two different procedures at different points of the 
        code, and it would be useful to know what mask this is. '''

        # retrieving mask level 4
        path = ("/idia/projects/hi_im/raw_vis/katcali_output/" + 
                "level4_output/mask/{}_{}_level4_mask".format(self.block,ant))
        mask = pickle.load(open(path,'rb'))
        
        # retrieving visibilities and masking (SARAO flags are not incorporated (?))
        path = "/idia/projects/hi_im/raw_vis/{}/{}/{}_{}".format(
            self.folder,self.block,self.block,ant)
        visH = pickle.load(open(path+"h_vis_data", "rb"), encoding="latin1")["vis"]
        visV = pickle.load(open(path+"v_vis_data", "rb"), encoding="latin1")["vis"]
        if masked:
            visH = np.ma.masked_equal(visH, 0)
            visV = np.ma.masked_equal(visV, 0)
    
        # retrieving gains
        path = "/idia/projects/hi_im/raw_vis/katcali_output/level3_output/{}_{}".format(self.block,ant)
        gainH = pickle.load(open(path + "h_level3_data","rb"), encoding="latin1")["gain_map"]
        gainV = pickle.load(open(path + "v_level3_data","rb"), encoding="latin1")["gain_map"]

        # cleaning outliers -- for now, substituted with a zero mask!
        if masked:  
            gainH = _clean_outliers(gainH)
            gainV = _clean_outliers(gainV)
            #gainH = np.ma.array(gainH, mask=mask['Inten_mask'])  # <-- Brandon doesn't seem to use it in his thesis
            #gainV = np.ma.array(gainV, mask=mask['Inten_mask'])
            #gainH = np.ma.masked_equal(gainH,0)
            #gainV = np.ma.masked_equal(gainV,0)
        return visH, visV, gainH, gainV, mask


    # -------------------------------------------------- #

    def get_frequency_bandpass(self, vis_min, smooth=None):
        ''' Determine the frequency bandpass from the raw visibility map. '''

        # estimating smooth parameters from noise -- for now not using this
        if smooth is None:
            diff = np.diff(vis_min)
            noise = 1.4826 * np.ma.median(np.ma.abs(diff-np.ma.median(diff))) / np.sqrt(2)
            smooth = vis_min.size * noise**2 * np.array([1000,200,50,50])
            print(smooth)

        # iteratively interpolating and clipping outliers
        weights = np.ones_like(vis_min)
        for s in smooth:
            func = sp.interpolate.UnivariateSpline(
                x=self.frequency_cut, y=vis_min, w=weights, k=5, s=s)
            res = vis_min - func(self.frequency_cut)
            clip = SigmaClip(sigma_upper=1, sigma_lower=20, maxiters=5)
            weights = (~clip(res).mask).astype(float)
    
        return func(self.frequency_cut)


    # -------------------------------------------------- #

    def combine_gain_curves(self, gain, bandpass, norm, freq_slice):
        """Replace a frequency range with the smooth gain curve and fit a spline."""

        # colapsing arrays into the necessary final quantities
        gain = np.ma.mean(gain,axis=0) / np.ma.max(np.ma.mean(gain,axis=0))
        bandpass = norm * bandpass / np.ma.max(bandpass)

        # get indexes in the interpolated and original array
        start_g = np.searchsorted(self.frequency, freq_slice[0])
        end_g = np.searchsorted(self.frequency, freq_slice[1])
        start_bp = np.searchsorted(self.frequency_cut, freq_slice[0])
        end_bp = np.searchsorted(self.frequency_cut, freq_slice[1])

        # get final combined gain curve
        gain_combined = np.ma.concatenate((
            gain[:start_g],bandpass[start_bp:end_bp], gain[end_g:]))

        # getting final interpolated gain curve
        valid = ~np.ma.getmaskarray(gain_combined)
        gain_final = sp.interpolate.UnivariateSpline(
            x=self.frequency[valid], y=gain_combined.data[valid], k=5, s=0.04)
        return gain_combined, gain_final

    
    # -------------------------------------------------- #

    def final_observations(self, ant, path_results):
        ''' Generates the final observations for a given antenna. '''

        # getting gain maps and initial quantities
        # (THESE ARE ALMOST THE SAME AS BEFORE, BUT NOW WITHOUT A LEVEL-4 MASK OR WITH ZEROS MASKED!)
        temps = []
        vis = []
        gains = []
        vis[0], vis[1], gainH[0], gainV[1] = self.get_gain_raws(ant, mask=False)

        for i in range(len(vis)):
            # getting gain curves
            gain_t = np.ma.mean(gains[i][self.nd_off, self.ifreq[0]:self.ifreq[1]], axis=1)
            gain_f = np.ma.mean(gains[i][self.nd_off, self.ifreq[0]:self.ifreq[1]], axis=0)
            bandpass = pickle.load(open(path_results + "{}_fbandpass.p".format(ant), "rb"))[i]

            # getting final observation
            div = (gain_t[:,None]/np.ma.mean(gain_t)) * (bandpass[None,:]/np.ma.max(gain_f))
            temps[i] = vis[i][self.nd_off, self.ifreq[0]:self.ifreq[1]] / div
            
        # get final observations
        obs = (temps[0] + temps[1]) / 2
        return obs


    # -------------------------------------------------- #

    def final_background(self, ant, path_results):
        ''' Adding all background temperature models. '''
        
        # Elevation temperature
        Tel = pickle.load(open(path_results + "{}_Tel.p", "rb"))
        Trec = pickle.load(open(path_results + "{}_Trec.p", "rb"))
        Tgal = pickle.load(open(path_results + "{}_Tgal.p", "rb"))

        # summing everything
        Tel = (Tel["H"] + Tel["V"]) / 2  # <-- WE'D DONE AN INTERPOLATION HERE BEFORE, ABOUT THE SPIKES!
        Trec = (Trec["H_interp"] + Trec["H_interp"]) / 2
        Tgal = (Tgal["H"] + Tgal["V"]) / 2
        Tcmb = 2.73
        return Tel + Trec + Tgal + Tcmb
        

    # -------------------------------------------------- #

    def get_constant_factor(self):

        # Noise models
        background_models = self.get_background_models(antenna=ant_name, pol=pol, mask_loc=mask_loc)
        return background_models

    