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
        s1_data_loc - Location of the re-calibration data
        s2_data_loc - Location of the angualr seperation maps of the satellite
        bias_choice_loc - Location of the bias choice parameters for the satellites
    """
    def __init__(self, 
                 file_name = None, 
                 sats_only = None,
                 s1_data_loc = '/idia/projects/hi_im/brandon/1551055211_level6_mask/', 
                 s2_data_loc = '/idia/projects/hi_im/brandon/1551055211_level6_mask/',
                 sat_cataloque_name = None,
                 bias_choice_loc = ''):
        
        self.file_name = file_name
        self.sats_only = sats_only
        self.s1_data_loc = s1_data_loc
        self.s2_data_loc =  s2_data_loc
        self.sat_catalogue = sat_cataloque_name
        self.bias_choice_loc = bias_choice_loc
        
        
        self.katdal_info = self.get_katdal_info(s1_data_loc)
        
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
        #------------------------------------------------------

        
        
    def excecute(self, obs_time_start=None, obs_time_end=None, 
                 obs_frequency_start=None, obs_frequency_end=None, file_bias_choice=None, add_sub=[None, None]):
        '''
        A function which excutes all the function currently available to us. 
        A means to avoid initializing them.
    
        obs_time_start/end - the time slice of the data and simulation
        obs_frequency_start/end - the frequency start and end for the data and simulations
        file_bias_choice - 1. is a str: file name, should be placed in the correct folder
                           2. is a list: the list should have the same number as constellations plus noise parameter
                           3. is None: user will then put amplitude choices for the constellation
        add_sub - a list. First None: add the BG model to the satellite data if !=None
                          Second None: subtracts the BG model from observation data if ==None
        '''
        
        
        # Sets the frequency band
        self.frequency_band = self.get_frequency_information()
        
        # Satellite positioning
        self.satellite_type, self.satellite_angle = self.get_satellite_angle_seperation() 
        
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
      
    
    
    def plotting(self, individual=None, logger=None, tod_limit=None, save_file=None, suffix=None):
        """
        Plotting various plots: 
        1. The 1D Simulation model vs the Observational data 
        2. The Time-Ordered-Data for the obsevational data
        3. The Time-Ordered-Data for the simualtion data
        
        Parameters:
        individual - If "None" will plot the combined model vs observation data. If "not None" will show the indivdiual satellite componants
        logger - If "None" plots will be in linear scale. If "not None" plots will be in log scale
        tod_limit - The vmin and vmax for both TOD maps
        sats_only - If you want to show the satellites alone
        save_file - If "not None" file will be saved for all plots. Plots name will include both time and freqeuncy positions.
        suffix - If "not None" plot name will contain user input suffix
        
              
        """
        self.slice_plot_frequency = self._get_slice_plot_(ALL=individual, save_file=save_file, log_scale=logger)
        self.sat_sim_map = self._get_TOD_sim_maps_(log_values=logger, vlimits=tod_limit, save_file=save_file)
        if self.sats_only == None:
            self.TOD_map = self._get_TOD_maps_(log_values=logger, vlimits=tod_limit, save_file=save_file)

    
        
    
    def get_katdal_info(self, s1_data_loc):
        '''
        Obtain KATDAL information regarding the data set such as the frequency and the noise diodes in scanning/no diode fired
        '''
        
        try:
            fname = self.file_name
            data = pickle.load(open(self.s1_data_loc+fname+'_katdal_info.p', 'rb'))
            
            return data
            
        except Exception as e:
            print fname+'-Katdal Information not found :('
        
        
        
        
    def get_frequency_information(self):
        '''
        Function for the frequency start and end postion
        !!! Should add some extra stuff here regarding the printing of the freqeuncy bands.
        For not fixed
        '''
        f_start_idx = 600
        f_end_idx = 2482
        f_band = self.frequency[f_start_idx:f_start_idx+f_end_idx]
        
        return f_band
        
               
        
    def get_calibration_data(self):
        '''
        Obtain the calibrated TOD for the temperature and the noise
        '''
        
        try:
            fname = self.file_name
            data = pickle.load(open(self.s1_data_loc+fname+'_average_TOD_BG_model.p'))
            
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
            data = pickle.load(open(self.s2_data_loc+fname+"_satellite_angular_position.p", "rb"))
            
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
                                     beam_model=self.satellite_angle[i], excel_sat=self.sat_catalogue)[0] for i, satellite_name in enumerate(self.satellite_type)])

        
        satellite_SED = np.array([gm.TOD_sats(name_tod=satellite_name, 
                                     fname=self.file_name, 
                                     frequency_tod=self.frequency_band, 
                                     beam_model=self.satellite_angle[i], excel_sat=self.sat_catalogue)[1] for i, satellite_name in enumerate(self.satellite_type)])
        
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
    
    
    # ------------------------------------PLOTS--------------------------------------
# **********************************************************************************************************
    # ------------------------------------PLOTS--------------------------------------

    def _get_slice_plot_(self, ALL=None, save_file=None, log_scale=None):
        '''
        Function for plotting the Simulation outputs
        '''        
        
        plt.figure(figsize=(14, 4))
        plt.title(self.file_name+': Time-['+str(np.round(self.nd_s0[self.time_idx[0]], 2))+'-'+str(np.round(self.nd_s0[self.time_idx[1]], 2))+'] seconds')
        
        plt.plot(self.frequency_band[self.frequency_idx[0]:self.frequency_idx[1]], self.simulation_slice, color='red', label='Model')      
        
        if self.sats_only==None:
            observation = self._average_over_frequency_(self.calibration_data_slice)
            plt.plot(self.frequency_band[self.frequency_idx[0]:self.frequency_idx[1]], observation, '-', color='black', label='Data')      
        
        plt.xlabel('Frequency [MHz]')
        plt.ylabel('Temperature [K]')
        if ALL!=None:
            for i in range(len(self.bias_choice)):
                plt.plot(self.frequency_band[self.frequency_idx[0]:self.frequency_idx[1]], 
                         self._average_over_frequency_(self.satellite_TOD_slice[i]) * self.bias_choice[i], 
                         label=self.satellite_type[i]+'  x'+str(self.bias_choice[i]))
            plt.ylim(bottom=1e-2)

        
        if log_scale==None:
            plt.yscale('log')
            plt.ylabel(r'log$_{10}$(Temperature [K])')
        
        
        plt.legend()
        plt.tight_layout()
        if save_file !=None:
            plt.savefig(self.s1_data_loc+self.file_name+'_'+str(np.round(self.nd_s0[self.time_idx[0]], 2))
                        +'_'+str(np.round(self.nd_s0[self.time_idx[1]], 2))+'.png')
            
            # Saving the data to file
            pickle.dump(observation, open(self.s1_data_loc+self.file_name+'_observation_'+str(np.round(self.nd_s0[self.time_idx[0]], 2))+
                            '_'+str(np.round(self.nd_s0[self.time_idx[1]], 2))+'_tod.p', 'wb'))
            
        else:
            plt.show()
        
        
   # Work in progress
    def _get_TOD_maps_(self, log_values=None, vlimits=None, save_file=None):
        '''
        Obtiaing the TOD maps for the different values for the OBSERVATION DATA
        '''
        

        extent = [self.nd_s0[self.time_idx[0]], self.nd_s0[self.time_idx[1]], 
                  self.frequency_band[self.frequency_idx[1]], self.frequency_band[self.frequency_idx[0]]]

        plt.figure()
        plt.title(self.file_name+'-Observation Data: Time-['+str(np.round(self.nd_s0[self.time_idx[0]], 2))+'-'+str(np.round(self.nd_s0[self.time_idx[1]], 2))+'] seconds')
        plt.xlabel('Time [s]')
        plt.ylabel('Frequency [MHz]')
        
        data_slice = self.calibration_data[self.frequency_idx[0]:self.frequency_idx[1], self.time_idx[0]:self.time_idx[1]]
        

        
        if log_values==None:
            if vlimits==None:
                hb=plt.imshow(np.log10(data_slice), extent=extent, aspect='auto')
            else:
                hb=plt.imshow(np.log10(data_slice), extent=extent, aspect='auto', vmin=vlimits[0], vmax=vlimits[1])
            
            cbar = plt.colorbar(hb)
            cbar.set_label(r'log$_{10}$(T) [K]', rotation=270, labelpad=20, y=0.45)

        else:
            if vlimits==None:
                hb=plt.imshow((data_slice), extent=extent, aspect='auto')
            else:
                hb=plt.imshow((data_slice), extent=extent, aspect='auto', vmin=vlimits[0], vmax=vlimits[1])
       
            cbar = plt.colorbar(hb)
            cbar.set_label(r'T [K]', rotation=270, labelpad=20, y=0.45)

        plt.tight_layout()
        if save_file !=None:
            plt.savefig(self.s1_data_loc+self.file_name+'_obs_data_'+str(np.round(self.nd_s0[self.time_idx[0]], 2))+
                        '_'+str(np.round(self.nd_s0[self.time_idx[1]], 2))+'.png')
            
            # Saving the data to file
            pickle.dump(data_slice, open(self.s1_data_loc+self.file_name+'_obs_data_'+str(np.round(self.nd_s0[self.time_idx[0]], 2))+
                            '_'+str(np.round(self.nd_s0[self.time_idx[1]], 2))+'_tod.p', 'wb'))
            
        else:
            plt.show()
            
            
            
   # Work in progress
    def _get_TOD_sim_maps_(self, log_values=None, vlimits=None, save_file=None):
        '''
        Obtiaing the TOD maps for the different values for the SIMULATION DATA
        log_values - 
        '''


        extent = [self.nd_s0[self.time_idx[0]], self.nd_s0[self.time_idx[1]], 
                  self.frequency_band[self.frequency_idx[1]], self.frequency_band[self.frequency_idx[0]]]

        plt.figure()
        plt.title(self.file_name+'-Simulation Data: Time-['+str(np.round(self.nd_s0[self.time_idx[0]], 2))+'-'+str(np.round(self.nd_s0[self.time_idx[1]], 2))+'] seconds')
        plt.xlabel('Time [s]')
        plt.ylabel('Frequency [MHz]')
        
        data_slice = self.simulation_TOD_slice
        

        
        if log_values==None:
            if vlimits==None:
                hb=plt.imshow(np.log10(data_slice), extent=extent, aspect='auto')
            else:
                hb=plt.imshow(np.log10(data_slice), extent=extent, aspect='auto', vmin=vlimits[0], vmax=vlimits[1])
            
            cbar = plt.colorbar(hb)
            cbar.set_label(r'log$_{10}$(T) [K]', rotation=270, labelpad=20, y=0.45)

        else:
            if vlimits==None:
                hb=plt.imshow((data_slice), extent=extent, aspect='auto')
            else:
                hb=plt.imshow((data_slice), extent=extent, aspect='auto', vmin=vlimits[0], vmax=vlimits[1])
       
            cbar = plt.colorbar(hb)
            cbar.set_label(r'T [K]', rotation=270, labelpad=20, y=0.45)

        plt.tight_layout()
        if save_file !=None:
            plt.savefig(self.s1_data_loc+self.file_name+'_sim_data_'+str(np.round(self.nd_s0[self.time_idx[0]], 2))+
                        '_'+str(np.round(self.nd_s0[self.time_idx[1]], 2))+'.png')
            
            # Saving the file
            pickle.dump(data_slice, open(self.s1_data_loc+self.file_name+'_sim_data_'+str(np.round(self.nd_s0[self.time_idx[0]], 2))+
                            '_'+str(np.round(self.nd_s0[self.time_idx[1]], 2))+'_tod.p', 'wb'))
        else:
            plt.show()


        
        
        
    