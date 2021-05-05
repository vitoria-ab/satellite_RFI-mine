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
                 obs_data_loc = '/idia/projects/hi_im/',
                 vis_data_loc = '/idia/projects/hi_im/raw_vis/',
                 gain_data_loc = '/idia/projects/hi_im/raw_vis/katcali_output/level3_output/'):
                
                
                self.folder_name = folder_name
                
                self.file_name = file_name
                
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
        
    #     sys.path.insert(2, '..//../My_files/')
        from wiggleZ_area import area
        area(fname)                                                                      # Calls a function to extract information from the data

        scan_time, scan_az, scan_el = np.load(fname+'_Time_Pos.npy')                     # Full "scan" time, Azimuth and Elevation positions

        nd_off_scan_data = np.load(fname+'_nd_S0.npy')                                   # Extracting the Noise diode "off" time and position
        nd_off_scan_pos, nd_off_scan = np.array(nd_off_scan_data[0], dtype='int64'), nd_off_scan_data[1]

        nd_off_in_st_pos = np.array([np.where(i==scan_time)[0][0] for i in nd_off_scan])         # Getting the position of the nd_0 in the scan time period
        
        print '1. Time for when noise diode off; \n2. The position when noise diode is off in the scan; \n3. Scan time; \n4. Az&El when noise diode is off during scan'
        return nd_off_scan-int(fname), nd_off_scan_pos, scan_time-int(fname), (scan_az[nd_off_in_st_pos], scan_el[nd_off_in_st_pos])
    
 

    def _conversion_rW_mK_(self, gain_map, visibility, antenna, pol, nd_off, frequency, c_start, c_end):

        fname = self.file_name
        ant_name = str(self.obs_data.ants[antenna])[0:4]

        # Mask
        path_2_masks = '/idia/projects/hi_im/raw_vis/katcali_output/level1_output/mask/'+str(fname)+'_'+ant_name+pol+'_mask'
        mask_load = pickle.load(open(path_2_masks, 'rb'))
        mask = mask_load['mask'][nd_off, c_start:c_end].T

        gain_time_mean = np.ma.mean(gain_map[nd_off, c_start:c_end], axis=1)
        # Saving a copy just in case
        a1_true = visibility[nd_off, c_start:c_end].T / gain_time_mean

        # Formula
        a1 = np.ma.array(visibility[nd_off, c_start:c_end].T, mask=mask) / gain_time_mean
        a2 = np.ma.mean(a1, axis=1)
        a3 = a2 / np.ma.mean(a2)

        #Getting the good channel list
        ch_list = np.where(a3.mask==False)[0]

        # Using RBF and getting the frequency bandpass
        rbf = Rbf(frequency[c_start:c_end][ch_list], a3[ch_list], smooth=100)
        freq_bandpass = rbf(frequency[c_start:c_end])

        temperature_tod = a1_true / freq_bandpass[:, None] #* 1000 # Units mKelvin     [What did we do here????]

        return temperature_tod, [frequency[c_start:c_end], freq_bandpass, ch_list], a1_true


    
    def TOD(self, ant_no,  nd_off, c_start, frequency=None, frequency_choice=1500, c_end=-1):
        '''
        Takes the information from "gain,vis data" and combines the HH VV together for a given frequency range.
        gain, visibility - gain data & visibility data respectivly 
        frequency - frequency [MHz]
        c_start, c_end - channel start and channel end for the data
        frequency_choice - user input slection of where the data output should end
        nd_off - the scan time 'position' where the noise diode should be off
        '''
        if frequency==None:
            frequency = self.freqs
                
        temperature_hh, bpass_hh, gain_time_mean_hh = self._conversion_rW_mK_(gain_map=self.get_gain_data(ant_no=ant_no)[0], 
                                                           visibility=self.get_vis_data(ant_no=ant_no)[0], 
                                                           antenna=ant_no, pol='h',
                                                           nd_off=nd_off,frequency=frequency, 
                                                           c_start=c_start, c_end=c_end)
        
        temperature_vv, bpass_vv, gain_time_mean_vv = self._conversion_rW_mK_(gain_map=self.get_gain_data(ant_no=ant_no)[1], 
                                                           visibility=self.get_vis_data(ant_no=ant_no)[1], 
                                                           antenna=ant_no, pol='v',
                                                           nd_off=nd_off, frequency=frequency, 
                                                           c_start=c_start, c_end=c_end)

        temperature_tod = ((temperature_hh)+(temperature_vv))/2

        freq_end = np.where(frequency[np.where(frequency > frequency_choice)[0][0]] == frequency[c_start:])[0][0]

        temperature_tod = temperature_tod[0:freq_end, :] * 1000   # Units now in [mK]

        return temperature_tod, bpass_hh, bpass_vv, freq_end, [temperature_hh, temperature_vv], [gain_time_mean_hh, gain_time_mean_vv]

