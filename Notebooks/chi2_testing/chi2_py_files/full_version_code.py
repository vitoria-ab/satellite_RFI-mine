'''
File for running lage data set of time chuks
'''
from satellite_RFI.src.satellite_sims import satellite_sim as ss
import time
import pickle
import astropy.units as u
from datetime import datetime
import tqdm
import os


import scipy as sp
import numpy as np
import pandas as pd
import scipy.optimize as opt
import matplotlib.pyplot as plt

import multiprocessing as mp
from threading import Thread

# ----------------------------------------------------------------------------------------#

obs_time_input=None
fname = '1551055211'


# Establishing the file name
if obs_time_input!=None:
    obs_time_in=[int(x) for x in obs_time_input.split()]
    obs_time = datetime(obs_time_in[0], obs_time_in[1], obs_time_in[2], obs_time_in[3], obs_time_in[4], obs_time_in[5])
    dt = obs_time.strftime('%Y-%m-%d %H:%M:%S')
    fname = int((obs_time - datetime(1970, 1, 1)).total_seconds())
else:
    dt = (datetime.utcfromtimestamp(float(fname)).strftime('%Y-%m-%d %H:%M:%S'))


# KATDAL information
katdal_info = pickle.load(open('/idia/projects/hi_im/brandon/1551055211/'+str(fname)+'_katdal_info.p', 'rb'), encoding='latin1')
info = [katdal_info[i] for i in katdal_info.keys()]

nd_s0=katdal_info['nd_s0']
nd_s0_coords=katdal_info['nd_s0_coords']
frequency=katdal_info['frequency']

# Frequuency band width [MHz]
fs=1000
fe=1500

# Folder for the day
folder = '2022_03_25'

# Save data paths
data_save='../data_test/'+str(fname)+'/pickle_info/'
if os.path.exists(data_save)==False:
    os.mkdir(data_save)

# MeerKAT data information
data_mkat = '../../../../Observation_results/Untangle/'+str(fname)+'/'

# Nearby constellation file
angle_val = '5'
nearby_constellation_path = '../nearby_satellite_mask/nearby_satellite_close_angle_'+angle_val+'.p'

# Constellation information
cons = [ 'GAL', 'BDS', 'GLO', 'GPS', 'SBAS', 'IRNSS']
bias = np.ones(len(cons))

# ----------------------------------------------------------------------------------------#

def radiometer_eq(data):
    '''
    Radiometer euquation for determining the error on the data
    '''
    d_nu = 0.2 * 10**6 # Hz
    d_t = 2 # s
    n_pol = 2 
    n_dish = 58
    sig2 = data**2 / (n_pol*d_nu*d_t*n_dish)
    sig = np.sqrt(sig2)
    
    return sig

# ----------------------------------------------------------------------------------------#

sat = ss(file_name=fname, sats_only=None, data_loc=data_mkat, sat_loc=data_mkat,
            survey_info=[nd_s0, nd_s0_coords, frequency], 
            sat_info='../../Satellite_simulations/Satellite_Catalogue/table3B_satellite_v3-1_reduced_2.csv',
            plots_loc='../data_test_plots/'+str(fname)+'/',
            sat_beam='emss_beam_r', frequency_range=[1000,1500], 
            constellations=cons, nearby_satellites=nearby_constellation_path)


np.random.seed()
dic = 10*np.random.random(sat.alpha_len)

sat.excecute(a_param=dic, obs_time_start=nd_s0[0], obs_time_end=nd_s0[-1], obs_frequency_start=1100, obs_frequency_end=1350, 
            file_bias_choice=bias, add_sub=[1, 1], band_lvl=[None, None], bandsize=None)

# ----------------------------------------------------------------------------------------#

# Chi2 
def chisq_func2(a_param):
    """
    Chi2 function which will take in all the parameters for the satellites
    """

    sat.excecute(a_param, obs_time_start=nd_s0[0], obs_time_end=nd_s0[-1], 
                 obs_frequency_start=1100, obs_frequency_end=1350, 
                 file_bias_choice=bias, add_sub=[1, 1], band_lvl=[None, None], bandsize=None)


    # Masked
    simulation = np.ma.array(data=sat.simulation_TOD_slice, mask=sat.mask_nearby_satellites_slice.T)
    data = np.ma.array(data=sat.calibration_data_slice, mask=sat.mask_nearby_satellites_slice.T)

    sig = 1#radiometer_eq(data=data)    

    chi_sq = np.ma.sum( (simulation - data )**2 / sig**2)
    # print (chi_sq)
    return chi_sq

# ----------------------------------------------------------------------------------------#

# Priors/Bounds
bnd_val = (0.0, 30)
bnds = [bnd_val for bnd_i in range(sat.alpha_len)]

# Optimization
# print ('Running optimization')
signal_PL = opt.minimize(fun=chisq_func2, 
                         x0=dic, 
                         method='Powell',
                         bounds=bnds, 
                         tol=1e-6, 
                         options={'maxiter':20})

# ----------------------------------------------------------------------------------------#

print ('Running 2nd init')
# 2nd initilization  
sat2 = ss(file_name=fname, sats_only=None, data_loc=data_mkat, sat_loc=data_mkat,
            survey_info=[nd_s0, nd_s0_coords, frequency], 
            sat_info='../../Satellite_simulations/Satellite_Catalogue/table3B_satellite_v3-1_reduced_2_shuffle.csv',
            plots_loc='../data_test_plots/'+str(fname)+'/',
            sat_beam='emss_beam_r', frequency_range=[1000,1500], 
            constellations=cons, nearby_satellites=nearby_constellation_path)

sat2.excecute(a_param=signal_PL.x, obs_time_start=nd_s0[0], obs_time_end=nd_s0[-1], 
              obs_frequency_start=1100, obs_frequency_end=1350, 
              file_bias_choice=bias, add_sub=[1, 1], band_lvl=[None, None], bandsize=None)

# ----------------------------------------------------------------------------------------#


data_info = {'initial':dic,
             'time': sat.nd_s0[0:-1],
             'best-fit':signal_PL.x,
             'chi2_value':signal_PL.fun,
             'chi2_div':signal_PL.fun/sat2.simulation_TOD_slice.size
}

pickle.dump(data_info, open('../data_test/'+str(fname)+'/data_info/parallel_'+folder+'/data_full_mask_'+angle_val+'.p', 'wb'))


#----------------------------------------------------------------------------------------#