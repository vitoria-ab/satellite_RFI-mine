import katdal
import katsdptelstate
KATSDPTELSTATE_ALLOW_PICKLE=1
import pickle
import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import scipy.signal as ss
import scipy as sp
import copy                                                  # Required when using Nan values and py2
from scipy.interpolate import Rbf
# Personal file constucted
from wiggleZ_area import area

font = {'family': 'serif',
'color':  'black',
'weight': 'normal',
'size': 18,
}

font_s = {'family': 'serif',
'color':  'black',
'weight': 'normal',
'size': 14,
}

class Data_reduction:
    def __init__(self,
                 folder_name = None,
                 file_name = None,
                 folder_output=None,
                 obs_data_loc = '/idia/projects/hi_im/',
                 vis_data_loc = '/idia/projects/hi_im/raw_vis/',
                 gain_data_loc = '/idia/projects/hi_im/raw_vis/katcali_output/level3_output/'):
                
                
                self.folder_name = folder_name
                
                self.file_name = file_name

                self.folder_output = folder_output
                
                self.vis_data_loc = vis_data_loc
                
                self.gain_data_loc = gain_data_loc
                
                self.obs_data = self.get_obs_data(obs_data_loc)
                
                self.freqs, self.timestamps =  self.freqs_and_time()                  
            
            
    def get_obs_data(self, obs_data_loc, user_input = None):
        '''
        Calling the full data set that is defined at some location
        obs_data_loc - Location of the full data set (.rdb files)
        '''
        data = None
        try:
            if user_input == None:
        
                fname = self.file_name
        
                data = katdal.open(obs_data_loc + self.folder_name+'/'+ fname+'/'+fname+'/'+fname+'_sdp_l0.full.rdb')
            
            else:
                data = katdal.open(user_input)
                
        except Exception as e:
            print 'File not found :('
        
        return data
    
    def freqs_and_time(self):
        '''
        Returns the frequency [MHz] and timestamps [seconds] from the data.rdb file
        '''
        data_file = self.obs_data                       # Defined in the function
        
        freqs = np.round(data_file.freqs / 1e6, 1 )                 # Frequency [MHz]
        time = data_file.timestamps  
        timestamps = data_file.timestamps - data_file.timestamps[0] # Timestamps for full data [seconds]

        return freqs, timestamps

    
    def get_vis_data(self, ant_no = 0):
        '''
        Locating and extracting the visibility information:
        vis_data_loc - Location of the visibility data;
        ant_no - The choice of antenna to look at
        '''
        vis_data_loc = self.vis_data_loc
        ant_name = str(self.obs_data.ants[ant_no])[0:4]
        
        recv_h = ant_name+'h'
        recv_v = ant_name+'v'  

        fname = self.file_name
        
        data_h = pickle.load(open(vis_data_loc + self.folder_name+'/'+fname+'/'+fname+'_'+recv_h+'_vis_data','rb'))
        data_v = pickle.load(open(vis_data_loc + self.folder_name+'/'+fname+'/'+fname+'_'+recv_v+'_vis_data','rb'))
        
        vis_h = data_h['vis']    # hh visibility

        vis_v = data_v['vis']    # vv visibility
        
        self.vis_name = ['HH','VV']
        
        return [vis_h,vis_v]
    
    
    def get_gain_data(self, ant_no = 0):
        '''
        Locating and extracting the gain information:
        gain_data_loc - Location of the gain data;
        ant_no - the choice of antenna
        '''
        gain_data_loc = self.gain_data_loc
        
        fname = self.file_name
        ant_name = str(self.obs_data.ants[ant_no])[0:4]
        recv_h = ant_name+'h'
        recv_v = ant_name+'v'  
        
        gain_data_h = pickle.load(open(gain_data_loc+'/'+fname+'_'+recv_h+'_level3_data'))    ## hh-pol
        gain_data_v = pickle.load(open(gain_data_loc+'/'+fname+'_'+recv_v+'_level3_data'))   ## vv-pol

        gain_map_h = gain_data_h['gain_map']
        gain_map_v = gain_data_v['gain_map']

        self.gain_name = ['HH-Gain', 'VV-Gain']
        
        return [gain_map_h, gain_map_v]
    
    
    def get_nd_times(self):
        '''
        A function to extract the positional and time (nd_scan time) positions for the scan period
        NOTE: this function is redundant, it's calling the .rdb file twice, must check again
        '''
        
        
        fname = self.file_name
        
        """Runs a the wiggleZ_area code in order to obtain the time positioning of the noise diodes"""
        area(fname=fname, file_path=self.folder_output)                                                     # Calls a function to extract information from the data

        scan_time, scan_az, scan_el = np.load(self.folder_output+fname+'_Time_Pos.npy')                     # Full "scan" time, Azimuth and Elevation positions

        nd_off_scan_data = np.load(self.folder_output+fname+'_nd_S0.npy')                                   # Extracting the Noise diode "off" time and position
        nd_off_scan_pos, nd_off_scan = np.array(nd_off_scan_data[0], dtype='int64'), nd_off_scan_data[1]

        nd_off_in_st_pos = np.array([np.where(i==scan_time)[0][0] for i in nd_off_scan])         # Getting the position of the nd_0 in the scan time period
        
        print '1. Time for when noise diode off; \n2. The position when noise diode is off in the scan; \n3. Scan time; \n4. Az&El when noise diode is off during scan'
        return nd_off_scan-int(fname), nd_off_scan_pos, scan_time-int(fname), (scan_az[nd_off_in_st_pos], scan_el[nd_off_in_st_pos])
    
 
        
    def get_background_models(self, antenna, pol, mask_loc):
        '''
        In order to quickly get the noise model values.
        antenna - the name of antenna m000
        pol - polarisations 
        mask_loc - the location of the results depending on the level of the mask used
        Returns the frequency shaped noise values
        '''
        if pol=='h':
            x = 'h-pol_interp'
            y = 'h-pol'
        elif pol=='v':
            x = 'v-pol_interp'
            y = 'v-pol'
        else:
            print 'Error wrong polarization'

        T_rec = np.mean(pickle.load(open(mask_loc+self.file_name+'_S1_'+antenna+'_t_rec.p', 'rb'))[x], axis=0)
        T_el = np.mean(pickle.load(open(mask_loc+self.file_name+'_S1_'+antenna+'_t_el.p', 'rb'))[x], axis=0)
        T_gal = np.mean(pickle.load(open(mask_loc+self.file_name+'_S1_'+antenna+'_t_gal.p', 'rb'))[y], axis=0)
        T_cmb = 2.73 
        
        # Index to say where the RFI free zone is
        data_idx = pickle.load(open(mask_loc+self.file_name+'_S1_'+antenna+'_t_rec.p', 'rb'))['v-pol idx']

        noise = T_rec + T_el + T_gal + T_cmb

        return noise, T_rec, T_el, T_gal, data_idx


    def conversion_rW_mK(self, antenna, pol, nd_off, frequency, c_start, c_end, mask_loc):

        if pol == 'h':
            x = 0
        else:
            x = 1

        gain_map=self.get_gain_data(ant_no=antenna)[x]
        visibility=self.get_vis_data(ant_no=antenna)[x]

        fname = self.file_name
        if isinstance(antenna, int) == True:
            ant_name = str(self.obs_data.ants[antenna])[0:4]
        else:
            ant_name = ant_no
            
#         print ant_name

        # Noise models
        background_models = self.get_background_models(antenna=ant_name, pol=pol, mask_loc=mask_loc)
        total_bg_models = background_models[0]
        rfi_free_idx = background_models[4]
        
        
        # Mask
        path_2_masks = '/idia/projects/hi_im/raw_vis/katcali_output/level1_output/mask/'+str(fname)+'_'+ant_name+pol+'_mask'
        mask_load = pickle.load(open(path_2_masks, 'rb'))
        mask = mask_load['mask'][nd_off, c_start:c_end]

        g_t = np.ma.mean(gain_map[nd_off, c_start:c_end], axis=1) 
        g_nu = np.ma.mean(gain_map[nd_off, c_start:c_end], axis=0) 

        # Try and see this adjustment here 
        # Saving a copy just in case, this contains the rfi section as well
        # a1_true = visibility[nd_off, c_start:c_end] / gain_time_mean             # Old
        a1_true = visibility[nd_off, c_start:c_end] * g_t[:, None]**-1    # New


        # Formula
        # a1 = np.ma.array(visibility[nd_off, c_start:c_end], mask=mask) / gain_time_mean     # Old
        a1 = np.ma.array(visibility[nd_off, c_start:c_end], mask=mask) * g_t[:, None]**-1 / total_bg_models   # New
        a2 = np.ma.mean(a1, axis=0)    # If using old==1, new==0
        a3 = a2 / np.ma.mean(a2)

        # #Getting the good channel list
        ch_list = np.where(a3.mask==False)[0]

        # Using RBF and getting the frequency bandpass
        rbf = Rbf(frequency[c_start:c_end][ch_list], a3[ch_list], smooth=100)
        freq_bandpass = rbf(frequency[c_start:c_end])

        temperature_tod = a1_true / freq_bandpass #* 1000 # Units mKelvin     [What did we do here????]

        return temperature_tod, [frequency[c_start:c_end], freq_bandpass, ch_list], [a1_true, a1], [g_t, g_nu], background_models

    
    def TOD(self, ant_no,  nd_off, c_start, mask_loc, frequency=None, frequency_choice=None, c_end=-1):
        '''
        Takes the information from "gain,vis data" and combines the HH VV together for a given frequency range.
        gain, visibility - gain data & visibility data respectivly 
        frequency - frequency [MHz]
        c_start, c_end - channel start and channel end for the data
        mask_loc - where the mask information sits for the background model data
        frequency_choice - user input slection of where the data output should end
        nd_off - the scan time 'position' where the noise diode should be off
        '''
        if frequency==None:
            frequency = self.freqs

        temperature_hh, bpass_hh, vis_gnu_h, gains_h, bg_models_h = self.conversion_rW_mK(antenna=ant_no, pol='h',
                                                                        nd_off=nd_off,frequency=frequency,
                                                                        c_start=c_start, c_end=c_end, mask_loc=mask_loc)

        temperature_vv, bpass_vv, vis_gnu_v, gains_v, bg_models_v = self.conversion_rW_mK(antenna=ant_no, pol='v',
                                                                        nd_off=nd_off,frequency=frequency,
                                                                        c_start=c_start, c_end=c_end, mask_loc=mask_loc)
        temperature_tod = ((temperature_hh)+(temperature_vv))/2

        freq_end = np.where(frequency[np.where(frequency > frequency_choice)[0][0]] == frequency[c_start:])[0][0]

        temperature_tod = temperature_tod[:, 0:freq_end]   # Units now in [K]

        return temperature_tod, [bpass_hh, bpass_vv], [temperature_hh, temperature_vv], [gains_h, gains_v], [bg_models_h[0], bg_models_v[0]], bg_models_h[4]

