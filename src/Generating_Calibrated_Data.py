import numpy as np
import pickle
import sys
from os import path
import os
from tqdm.notebook import tqdm
import numpy.ma as ma

from data_reduction import *


###############################################

fname = str(sys.argv[1])   

# 1551037708   done
# 1551055211   done
# 1553966342   
# 1554156377   done
# 1556052116
# 1556138397
# 1562857793

if fname == '1551037708' or fname == '1551055211' or fname == '1553966342' or fname=='1554156377':
    folder = 'SCI-20180330-MS-01'
    
if fname == '1555775533' or fname =='1555793534' or fname =='1555861810' or fname =='1556034219' or fname =='1556052116' or fname =='1556120503' or fname =='1556138397' or fname =='1555879611' or fname =='1561650779':
    folder = 'SCI-20190418-MS-01'
    
if fname == '1562857793':
    folder = ''


dat1 = Data_reduction(file_name = fname, folder_name = folder)

##################################################

# Checking if the KATDAL Information is already available, 
# if not running the process to obtain
if path.exists(fname+'_katdal_info.p'):
    print 'Files already exists, data is pulled'
    katdal_info = pickle.load(open(fname+'_katdal_info.p', 'rb'))

    nd_s, nd_s0, freqs, nd_s0_pos, timestamps, nd_s0_coords, nd_s0_coords2 = [katdal_info[i]
                                                               for i in katdal_info.keys()]

else:
    nd_s0, nd_s0_pos, nd_s, nd_s0_coords, nd_s0_coords2 = dat1.get_nd_times()     # nd_s0_coords is Az and El and nd_s0_coords2 contains the RA and DEC

    freqs, timestamps = dat1.freqs, dat1.timestamps

    # Pickling the inforamation from dat1 been pickles
    katdal_info = {"nd_s0":nd_s0, 
                   "nd_s0_pos":nd_s0_pos,
                   "nd_s":nd_s,
                   "nd_s0_coords":nd_s0_coords,
                   "nd_s0_coords2":nd_s0_coords2,
                   "frequency":freqs,
                   "time":timestamps 
    }

    pickle.dump(katdal_info, open(fname+'_katdal_info.p', 'wb'))
    
#######################################################################

'''Calculating the TOD values for antennae and their bandpass 
in the hh and vv'''

if path.exists(fname+'_calibrated_antennae_data.p'):
    print 'Files already exists, data is pulled'
    tod = pickle.load(open(fname+'_calibrated_antennae_data.p', 'rb'))
    
    good_antennae = tod['ant']
    temperature_tod = tod['cali_tod']
    
else:
    print 'Data does not exist'
    temperature_ = []
    b_pass_hh = []
    b_pass_vv = []
    good_antennae = []

    # for i in tqdm(range(len(dat1.obs_data.ants)), unit='ant'):
    for i in tqdm(range(0, 60, 1), unit='ant'):
        try: 
            TOD = dat1.TOD(ant_no=i, nd_off=nd_s0_pos, c_start=600)
            temperature_.append(TOD[0])
            b_pass_hh.append(TOD[1])
            b_pass_vv.append(TOD[2])


        except IOError:
            print 'Antenna - '+str(dat1.obs_data.ants[i])[0:4]+' data missing'
            continue
            
        except ValueError:
            print 'Antenna - '+str(dat1.obs_data.ants[i])[0:4]+' zero-size array to reduction operation maximum which has no identity'
            continue
        else:
            good_antennae.append(str(dat1.obs_data.ants[i])[0:4])

    frequency_end_pos = TOD[3]
    temperature_tod = np.array(temperature_)
    
    cali_tod = {
        'ant': np.array(good_antennae),
        'cali_tod': temperature_tod,  
        'freq_end_pos': frequency_end_pos
    }

    pickle.dump(cali_tod, open(fname+'_calibrated_antennae_data.p', 'wb'))

    
cali_tod = {}

###########################################################

# Loading the calibrated data
cali_data = pickle.load(open(fname+'_calibrated_antennae_data.p', 'rb'))


# Getting the keys from the data 
good_antennae = np.array(cali_data['ant'])

temperature_tod = cali_data['cali_tod']

###########################################################

'''Fix here this 2482'''
frequency_end_pos = 2482
freq_band = freqs[600:frequency_end_pos+600]

###########################################################

# Location of the mask data
loc = '/idia/projects/hi_im/raw_vis/katcali_output/'

t_rec_h, t_rec_v = [], []
t_gal_h, t_gal_v = [], []
t_map_h, t_map_v = [], []

d4_mask_list = [] 
# Loop that runs through all the t_rec info
for ant_no, i in enumerate(tqdm(good_antennae, unit='ant')):
    # checking to see if the masks exist or not and re-writting the code
    try:
        # Lvl 3 mask
        d3_h = pickle.load(open(loc+'level3_output/'+str(fname)+'_'+i+'h_level3_data'))
        d3_v = pickle.load(open(loc+'level3_output/'+str(fname)+'_'+i+'v_level3_data'))

    except IOError:
        print 'Antenna - '+i+' Lvl-3 mask missing'
        good_antennae = np.delete(good_antennae, ant_no)
        temperature_tod = np.delete(arr=temperature_tod, obj=ant_no, axis=0)
        continue
        
    try:
        # Lvl 4 mask
        d4_mask = pickle.load(open(loc+'level4_output/mask/'+str(fname)+'_'+i+'_level4_mask'))
        d4_mask_list.append(d4_mask['Inten_mask'][nd_s0_pos, 600:frequency_end_pos+600].T)
        
    except IOError:
        print 'Antenna - '+i+' Lvl-4 mask missing'
        good_antennae = np.delete(good_antennae, ant_no)
        temperature_tod = np.delete(arr=temperature_tod, obj=ant_no, axis=0)
        continue

    # T_rec information
    t_rec_h.append(d3_h['Tsm_map'][nd_s0_pos, 600:frequency_end_pos+600].T)
    t_rec_v.append(d3_v['Tsm_map'][nd_s0_pos, 600:frequency_end_pos+600].T)
    
    # T_gal information
    t_gal_h.append(d3_h['Tgal_map'][nd_s0_pos, 600:frequency_end_pos+600].T)
    t_gal_v.append(d3_v['Tgal_map'][nd_s0_pos, 600:frequency_end_pos+600].T)
    
    # T_map information
    t_map_h.append(d3_h['T_map'][nd_s0_pos, 600:frequency_end_pos+600].T)
    t_map_v.append(d3_v['T_map'][nd_s0_pos, 600:frequency_end_pos+600].T)
    
t_rec_h = np.ma.array(t_rec_h)
t_rec_v = np.ma.array(t_rec_v)

t_gal_h = np.ma.array(t_gal_h)
t_gal_v = np.ma.array(t_gal_v)

t_map_h = np.ma.array(t_map_h)
t_map_v = np.ma.array(t_map_v)

d4_mask = np.array(d4_mask_list)

########################################################

# Updatting the list
cali_data['ant'] = good_antennae
cali_data['cali_tod'] = temperature_tod

# Checking the data and saving it
if os.path.exists(fname+'_calibrated_antennae_data.p'):
    os.remove(fname+'_calibrated_antennae_data.p')
    pickle.dump(cali_data, open(fname+'_calibrated_antennae_data.p', 'wb'))

########################################################

## Getting T_rec-------------------------------


# Getting the mean of all antennae
t_rec_h_avg = np.ma.median(t_rec_h, axis=0)
t_rec_v_avg = np.ma.median(t_rec_v, axis=0)

# Averaging across time for the mean antennae
t_rec_h_across_t = np.ma.median(t_rec_h_avg, axis=0)
t_rec_v_across_t = np.ma.median(t_rec_v_avg, axis=0)

# Getting the mask for level 4 for the different antennae
t_rec_h_l4, t_rec_v_l4 = [], []
for i in range(t_rec_h.shape[0]):
    t_rec_h_l4.append(np.ma.masked_array(t_rec_h[i], mask=d4_mask[i]))
    t_rec_v_l4.append(np.ma.masked_array(t_rec_v[i], mask=d4_mask[i]))

t_rec_h_l4 = np.ma.array(t_rec_h_l4)
t_rec_v_l4 = np.ma.array(t_rec_v_l4 )

# Getting the median of all antennae
t_rec_h_avg_l4 = np.ma.median(t_rec_h_l4, axis=0)
t_rec_v_avg_l4 = np.ma.median(t_rec_v_l4, axis=0)

# Getting the frequency list for RBF interpolation
t_rec_h_avg_l4_freq = np.ma.median(t_rec_h_avg_l4, axis=1)
t_rec_v_avg_l4_freq = np.ma.median(t_rec_v_avg_l4, axis=1)

'''Change up, switching from using the first timestamp to using the average timestamp'''
freq_trec_h_list = np.where(t_rec_h_avg_l4_freq.mask==False)[0]
freq_trec_v_list = np.where(t_rec_v_avg_l4_freq.mask==False)[0]

#Reset the memory
t_rec_h = 0
t_rec_v = 0

#############################################################

# Using RBF-linear as it seems to be the best
'''Reason for linear can be found in JNote version 1 calculations'''
rbf_lin_h = Rbf(freq_band[freq_trec_h_list], 
                t_rec_h_avg_l4_freq[freq_trec_h_list], function='linear')

rbf_lin_v = Rbf(freq_band[freq_trec_v_list], 
                t_rec_v_avg_l4_freq[freq_trec_v_list], function='linear')

# Interpolating over the full frequency band
t_rec_h_f_interp = rbf_lin_h(freq_band)[:, None]
t_rec_v_f_interp = rbf_lin_v(freq_band)[:, None]

# Setting up the time and normalizing it
t_rec_h_across_t_norm = t_rec_h_across_t[None, :] / np.max(t_rec_h_across_t)
t_rec_v_across_t_norm = t_rec_v_across_t[None, :] / np.max(t_rec_v_across_t)

# New TOD interpolated
t_rec_h_TOD = t_rec_h_f_interp * t_rec_h_across_t_norm
t_rec_v_TOD = t_rec_v_f_interp * t_rec_v_across_t_norm

# Combining polarisations together
t_rec_TOD = (t_rec_h_TOD+t_rec_v_TOD)/2

# t_rec_tod_across_nu = np.ma.mean(t_rec_TOD, axis=1)

###################################################################

# Getting T_gal ------------------------------

t_gal_h_avg = np.ma.median(t_gal_h, axis=0)
t_gal_v_avg = np.ma.median(t_gal_v, axis=0)

t_gal_TOD = (t_gal_h_avg + t_gal_v_avg) / 2

t_gal_h = 0
t_gal_v = 0

###################################################################

# We have a script in this location that runs for the blocks T_el
tel_loc = '/users/bengelbrecht/PhD_Work/Satellite_Code/My_files_2/Work_in_progress/T_elevation_jobs/



t_el_h, t_el_v = [], []
for i in tqdm(good_antennae): # Error missing m031
# for i in tqdm(range(60)):
    d_h = pickle.load(open(tel_loc+fname+'_'+i+'h_full_t_el', 'rb'))
    d_v = pickle.load(open(tel_loc+fname+'_'+i+'v_full_t_el', 'rb'))

    t_el_h.append(d_h['Tel_map'][600:frequency_end_pos+600, nd_s0_pos] * 1000)
    t_el_v.append(d_v['Tel_map'][600:frequency_end_pos+600, nd_s0_pos] * 1000)
    
t_el_h = np.ma.array(t_el_h)
t_el_v = np.ma.array(t_el_v)

t_el_h_avg =  np.ma.median(t_el_h, axis=0)
t_el_v_avg =  np.ma.median(t_el_v, axis=0)

t_el = (t_el_h_avg + t_el_v_avg)/2


# Finding spikes in the data
threshold_no = 2

try:
    s_point = np.where(abs(t_el[0,1:] - t_el[0,0:-1]) > threshold_no)[0][0]
    e_point = np.where(abs(t_el[0,1:] - t_el[0,0:-1]) > threshold_no)[0][-1]

    area_of_interest = np.arange(s_point, e_point+1, 1)

    # Making a mask for the area
    masking_area = np.zeros(t_el.shape)
    masking_area[:, area_of_interest] = 1

    # New T_el
    t_le_masked = ma.masked_array(t_el, mask=masking_area)

    # Deleting area of interests
    t_le_masked_across_t = np.delete(t_le_masked[0], area_of_interest)
    nd_s0_2 = np.delete(nd_s0, area_of_interest)

    # RBF  in the temporal 
    rbf_tle_time = Rbf(nd_s0_2, t_le_masked_across_t)

    # The frequency dependance, nomralized
    tle_freq = t_le_masked[:, 0] / np.ma.max(t_le_masked[:, 0])

    # Final T_le
    t_el_final = tle_freq[:, None] * rbf_tle_time(nd_s0)[None, :] / 1000    #[K]
    
except IndexError:
    print 'Data has no spikes'
    
    # Final T_le
    t_el_final = t_el / 1000    #[K]
    
########################################################################

# CMB Temperature
T_cmb = 2.73 #[K]

########################################################################

d = {}
d['T_TOD'] = temperature_tod_avg
d['T_rec'] = t_rec_TOD
d['T_gal'] = t_gal_TOD
d['T_el'] = t_el_final
d['T_noise'] = T_noise

fs=open(fname+'_S1_Noise_contibution.p','wb')
pickle.dump(d,fs,protocol=2)
fs.close()

#######################################################################

print ('Success')