from satellite_RFI.src import gnss_models_v3 as gm
import pickle
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec
from tqdm.notebook import tqdm

class satellite_sim:
    """
    An object which calculates the comparison between the Observational TOD and the simulated TOD.
    The TOD can be sliced in both time and frequency for the users preferance.
    
    Requirements:
        file_name - file name 
        sats_only - Include or exclude observational data set to !=None
        s_data_loc - Location of the re-calibration data and angualr seperation maps of the satellite
        sat_beam - The beam choice applied for the data eg: [emss_beam]
        bias_choice_loc - Location of the bias choice parameters for the satellites
    """
    def __init__(self, 
                 file_name=None, 
                 sats_only=None,
                 s_data_loc=None, 
                 plots_loc=None,
                 sat_catalogue_name=None,
                 sat_catalogue_loc=None,
                 sat_beam=None,
                 frequency_range=None,
                 bias_choice_loc=''):
        
        self.file_name=file_name
        self.sats_only=sats_only
        self.s_data_loc=s_data_loc
        self.plots_loc=plots_loc
        self.sat_catalogue=sat_catalogue_name
        self.sat_catalogue_loc=sat_catalogue_loc
        self.sat_beam = sat_beam
        self.frequency_choice=frequency_range
        self.bias_choice_loc=bias_choice_loc
                
        self.katdal_info=self.get_katdal_info(s_data_loc)
        
        #------------------------------------------------------
        # Getting the outputs of katdal info:
        self.nd_s, self.nd_s0, self.frequency, self.nd_s0_pos, self.timestamps, self.nd_s0_coords = [self.katdal_info[i] for i in self.katdal_info.keys()]
        '''
        nd_s - noise diode scan in period
        nd_s0 - noise diode off scan in period
        frequency - frequency range or band
        nd_s0_pos - index of noise diode off in scan perid
        timestamps - time flow od the data
        nd_s0_coords - azimuth and elevation of the data
        '''
        
        # Satellite positioning
        self.satellite_type, self.satellite_angle = self.get_satellite_angle_seperation()
        #------------------------------------------------------

        
        
    def excecute(self, obs_time_start=None, obs_time_end=None, 
                 obs_frequency_start=None, obs_frequency_end=None, frequency_idx=None, 
                 file_bias_choice=None, add_sub=[None, None], band_lvl=[None, None]):
        '''
        A function which excutes all the function currently available to us. 
        A means to avoid initializing them.
    
        obs_time_start/end - the time slice of the data and simulation
        obs_frequency_start/end - the frequency start and end for the data and simulations
        file_bias_choice - 1. is a str: file name, should be placed in the correct folder
                           2. is a list: the list should have the same number as constellations plus noise parameter
                           3. is None: user will then put amplitude choices for the constellation
        frequency_idx - The minimum and maximum idx for the frequency band (user defined)
        add_sub - a list. First None: add the BG model to the satellite data if !=None
                          Second None: subtracts the BG model from observation data if ==None
        band_lvl - the bandwidth of the signal and the level of attenuation, default=[None,None]
        '''
        
        
        # Sets the frequency band
        self.frequency_band = self.get_frequency_information() 
        
        # Bandwith and level of difference for attenuation
        self.band_lvl = band_lvl
        
        # Satellite TOD
        self.satellite_TOD, self.satellite_SED = self.get_gnss_simulaton()
        
        # BG Noise: subtract the observational data; add to the simulations
        self.add_BG,  self.sub_BG = add_sub
        
        
        # Slice idx in the frequency and the time
        self.time_idx, self.frequency_idx = self.get_slice_idx(start_time=obs_time_start, 
                                                                    end_time=obs_time_end, 
                                                                    start_frequency=obs_frequency_start, 
                                                                    end_frequency=obs_frequency_end)
        
#         if self.sats_only==None:
#             """
#             sats_only != None: Allows for the observational data to be used
#             """
        # Observational data
        self.calibration_data, self.calibration_data_original, self.calibration_data_noise = self.get_calibration_data()

        # Calibration data slice
        self.calibration_data_slice, self.calibration_noise_slice = self.get_data_slice()

        
        # Satellite simulation slice
        self.simulation_slice, self.simulation_TOD_slice, self.bias_choice, self.satellite_TOD_slice = self.get_simulation_slice(file_bias_choice=file_bias_choice)
      
    
   
    def get_katdal_info(self, s_data_loc):
        '''
        Obtain KATDAL information regarding the data set such as the frequency and the noise diodes in scanning/no diode fired
        '''
        
        try:
            fname = self.file_name
            data = pickle.load(open(self.s_data_loc+fname+'_katdal_info.p', 'rb'))
            
            return data
            
        except Exception as e:
            print fname+'-Katdal Information not found :('
        
        
        
        
    def get_frequency_information(self):
        '''
        Function for the frequency start and end postion
        !!! Should add some extra stuff here regarding the printing of the freqeuncy bands.
        For not fixed
        '''
        f_start_idx = (np.where(self.frequency > self.frequency_choice[0])[0][0])
        f_end_idx = (np.where(self.frequency > self.frequency_choice[1])[0][0])
#         f_start_idx = 600
#         f_end_idx = 2482
        f_band = self.frequency[f_start_idx:f_end_idx]
        
        return f_band
        
               
        
    def get_calibration_data(self):
        '''
        Obtain the calibrated TOD for the temperature and the noise
        '''
        
        try:
            fname = self.file_name
            data = pickle.load(open(self.s_data_loc+fname+'_average_TOD_BG_model.p'))
            
            Temp_tod = data['TOD Avg'].T
            Temp_noise = data['BG Model'].T
            
            if self.sub_BG==None:
                Temp_res = Temp_tod - Temp_noise     # Getting the BG model to be added to the simualtions instead
            else:
                Temp_res = Temp_tod
                
            return Temp_res, Temp_tod, Temp_noise

        except Exception as e:
            print fname+'-Calibration Information not found :('
       
        
           
    def get_satellite_angle_seperation(self):
        '''
        Obtain the angular seperation results for the various satellites
        This takes 9sec to read in
        '''
        
        try:
            fname = self.file_name
            beam_choice = self.sat_beam
            data = pickle.load(open(self.s_data_loc+fname+'_satellite_angular_position_'+beam_choice+".p", "rb"))
            
            Satellite_type = data["sat_name"]     # Contains the names of the constellations
            Satellite_angle = data["angular"]     # Contains the angular seperation maps
            
            return Satellite_type, Satellite_angle
        
        except Exception as e:
            print fname+'-Satellite angular seperation not found :('
                        
        
    def get_gnss_simulaton(self):
        '''
        Get the TOD maps of the satellites and our data.
        For all the different types of satellites
        '''
        from gnss_models_v3 import TOD_sats
        
        satellite_TOD = np.array([gm.TOD_sats(name_tod=satellite_name, 
                                     fname=self.file_name, 
                                     frequency_tod=self.frequency_band, 
                                     beam_model=self.satellite_angle[i], band_lvl=self.band_lvl, excel_sat=self.sat_catalogue,
                                             excel_cat_loc=self.sat_catalogue_loc)[0] for i, satellite_name in enumerate(self.satellite_type)])

        
        satellite_SED = np.array([gm.TOD_sats(name_tod=satellite_name, 
                                     fname=self.file_name, 
                                     frequency_tod=self.frequency_band, 
                                     beam_model=self.satellite_angle[i], band_lvl=self.band_lvl, excel_sat=self.sat_catalogue,
                                             excel_cat_loc=self.sat_catalogue_loc)[1] for i, satellite_name in enumerate(self.satellite_type)])
        
        return satellite_TOD, satellite_SED
    
    
    
    #-------------------------------------------S4-----------------------------------------------------------------
    #                                         SECTION 4
    #-------------------------------------------S4-----------------------------------------------------------------

    def get_slice_idx(self, start_time=None, end_time=None, start_frequency=None, end_frequency=None):
        '''
        A function that provides the idx that you wish to slice from
        start_time - the beginning of the scan period - 774 seconds
        end_time - the end of the scan period - 6474 seconds
        start_frequency - beginning of the freqeuncy band usually 981 MHz
        end_frequency - end of the frequency band usually 1499.9
        '''   
        
        # Slicing in the time domain:
        if start_time==None and end_time==None:
            st_pos, et_pos = 0,-1
        else:
            st_pos = (np.where(self.nd_s0 > start_time)[0][0])
            et_pos = (np.where(self.nd_s0 > end_time)[0][0])
            print 'Time between: '+str(self.nd_s0[st_pos])+' and '+str(self.nd_s0[et_pos])+' in seconds\n'
            
            
        # Slicing in the frequency domain:
        if start_frequency==None and end_frequency==None:
            sf_pos, ef_pos = 0,-1
        else:
            sf_pos = (np.where(self.frequency_band > start_frequency)[0][0])
            ef_pos = (np.where(self.frequency_band > end_frequency)[0][0])
            print 'Frequency between: '+str(self.frequency_band[sf_pos])+' and '+str(self.frequency_band[ef_pos])+' in MHz\n'
            
        return (st_pos, et_pos), (sf_pos, ef_pos)
    
    
    def get_data_slice(self):
        """
        A function that slices the observational data based on the users input of frequency and time points
        """
        calibration_data_slice = self.calibration_data[self.frequency_idx[0]:self.frequency_idx[1], self.time_idx[0]:self.time_idx[1]]
        calibration_noise_slice = self.calibration_data_noise[self.frequency_idx[0]:self.frequency_idx[1], self.time_idx[0]:self.time_idx[1]]
        
        return calibration_data_slice, calibration_noise_slice
      
    
    
    def _average_over_time_(self, x):
        '''
        Function to return the averaged time response
        from a 2d shape, time should be in the first axis
        '''
        return np.mean(x, axis=0)

    
    
    def _average_over_frequency_(self, x):
        '''
        Function to return the averaged frequency response
        from a 2d shape
        '''
        return np.mean(x, axis=1)
    
    
    
    
    def get_simulation_slice(self, file_bias_choice=None):
        '''
        Slicing the simualted satellite data with the index values obtained from the 'get_data_sliced'
        
        '''
#       This is needs to spliced with the above slice
        satellite_TOD_slice = self.satellite_TOD[:, self.frequency_idx[0]:self.frequency_idx[1], self.time_idx[0]:self.time_idx[1]]    
           
        if type(file_bias_choice)==str:
            bias_choice = np.loadtxt(fname=self.bias_choice_loc+(file_bias_choice)+'.txt', delimiter=' ')
        
        elif type(file_bias_choice)==list:
            print 'Bias choice is follows:'+', '.join(self.satellite_type) +', noise'
            bias_choice = file_bias_choice
        
        else:
            print  'Enter the '+str(len(self.satellite_type)+1)+' bias choices for the following: '
            print ', '.join(self.satellite_type) +', noise'
            bias_choices_input = raw_input('Enter elements of a list separated by space ')
            bias_choice = [int(i) for i in bias_choices_input.split()]
        
        
        gnss_bias_model = np.nansum([satellite_TOD_slice[i]*bias_choice[i] for i in range(len(satellite_TOD_slice))], 0) #+ bias_choice[-1] Don't require this amplitude
        
        
        #Threshold ---------------------------------------
        threshold_k = 400   # K
#         gnss_bias_model_m = np.ma.masked_where(gnss_bias_model >=threshold_k, gnss_bias_model)     # Old method of masking the values, 
                                                                                                     # NOTE have to change the the variable name to have 'xxx_m'
        gnss_bias_model[gnss_bias_model >= threshold_k] = threshold_k                              # Adding a new threshold method 
#         satellite_TOD_slice[satellite_TOD_slice >= threshold_k] = threshold_k                        # Setting the threshold before bias choice
        # ----------------------------------------------
        
        if self.add_BG==None:
            gnss_bias_model_m = gnss_bias_model 
        else:
            gnss_bias_model_m = gnss_bias_model + self.calibration_noise_slice
               
       
        gnss_bias_model_frequency = self._average_over_frequency_(gnss_bias_model_m)

        
        
        return gnss_bias_model_frequency, gnss_bias_model_m, bias_choice, satellite_TOD_slice
    
 

        
        
        
    